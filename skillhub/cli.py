"""CLI `skill` do SkillHub.

Comandos V1:
    skill create <name>          cria o esqueleto da skill
    skill validate [name]        valida uma ou todas as skills
    skill list                   lista as skills com versão/owner/status
    skill version <name>         mostra a versão atual
    skill bump <name> <part>     sobe major/minor/patch e atualiza CHANGELOG
    skill registry               regenera registry/registry.json
    skill build                  monta o plugin (plugins/vec-skills/) do marketplace
    skill publish <name>         valida + bump opcional + registry + build + commit/push/tag/release
"""

from __future__ import annotations

from pathlib import Path

import typer

from . import core

app = typer.Typer(
    add_completion=False,
    help="SkillHub - gerenciador de skills do Claude Code da VEC.",
    no_args_is_help=True,
)


def _root() -> Path:
    try:
        return core.find_repo_root()
    except FileNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(1)


# --- create ----------------------------------------------------------------

SKILL_MD_TEMPLATE = """---
name: {name}
description: {description}
---

# {name}

Descreva aqui o que a skill faz e quando o Claude deve usá-la.

## Quando usar
- ...

## Passos
1. ...
"""

CHANGELOG_TEMPLATE = """# Changelog - {name}

Todas as mudanças relevantes desta skill.
O formato segue [Keep a Changelog](https://keepachangelog.com/) e Semver.

## [{version}] - inicial
### Added
- Versão inicial da skill.
"""

SMOKE_TEST_TEMPLATE = """# Teste de fumaça - {name}

Cenário mínimo para validar que a skill dispara e responde como esperado.

**Prompt de exemplo:** "..."
**Resultado esperado:** ...
"""


@app.command()
def create(
    name: str = typer.Argument(..., help="Nome da skill (kebab-case)."),
    owner: str = typer.Option("growth", help="Time dono da skill."),
    description: str = typer.Option("TODO: descreva a skill.", help="Descrição curta."),
):
    """Cria o esqueleto de uma skill nova."""
    root = _root()
    if not core.SKILL_NAME_RE.match(name):
        typer.secho(
            f"Nome inválido '{name}'. Use minúsculas, números e hífen (ex: planner).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    sp = core.skill_path(root, name)
    if sp.exists():
        typer.secho(f"Skill '{name}' já existe em {sp}", fg=typer.colors.RED)
        raise typer.Exit(1)

    (sp / "tests").mkdir(parents=True, exist_ok=True)
    (sp / "SKILL.md").write_text(
        SKILL_MD_TEMPLATE.format(name=name, description=description), encoding="utf-8"
    )
    meta = core.SkillMeta(
        name=name, version="1.0.0", owner=owner, status="draft", description=description
    )
    core.save_skill_meta(root, meta)
    (sp / "CHANGELOG.md").write_text(
        CHANGELOG_TEMPLATE.format(name=name, version="1.0.0"), encoding="utf-8"
    )
    (sp / "tests" / "smoke.md").write_text(
        SMOKE_TEST_TEMPLATE.format(name=name), encoding="utf-8"
    )

    typer.secho(f"Skill '{name}' criada em {sp.relative_to(root)}", fg=typer.colors.GREEN)
    typer.echo("Edite SKILL.md, ajuste skill.yaml e rode: skill validate " + name)


# --- validate --------------------------------------------------------------


@app.command()
def validate(
    name: str = typer.Argument(None, help="Skill a validar (vazio = todas)."),
):
    """Valida a estrutura e os metadados de uma ou de todas as skills."""
    root = _root()
    targets = [name] if name else core.list_skill_names(root)
    if not targets:
        typer.secho("Nenhuma skill encontrada em skills/.", fg=typer.colors.YELLOW)
        raise typer.Exit(0)

    total_errors = 0
    for skill in targets:
        errors = core.validate_skill(root, skill)
        if errors:
            total_errors += len(errors)
            typer.secho(f"[X] {skill}", fg=typer.colors.RED, bold=True)
            for e in errors:
                typer.echo(f"    - {e}")
        else:
            typer.secho(f"[OK] {skill}", fg=typer.colors.GREEN)

    if total_errors:
        typer.secho(f"\n{total_errors} problema(s) encontrado(s).", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho("\nTudo válido.", fg=typer.colors.GREEN)


# --- list ------------------------------------------------------------------


@app.command(name="list")
def list_skills():
    """Lista as skills com versão, owner e status."""
    root = _root()
    names = core.list_skill_names(root)
    if not names:
        typer.secho("Nenhuma skill em skills/.", fg=typer.colors.YELLOW)
        return
    typer.echo(f"{'SKILL':<24} {'VERSAO':<9} {'OWNER':<12} STATUS")
    typer.echo("-" * 60)
    for name in names:
        try:
            m = core.load_skill_meta(root, name)
            typer.echo(f"{name:<24} {m.version:<9} {m.owner:<12} {m.status}")
        except Exception as exc:  # noqa: BLE001
            typer.secho(f"{name:<24} (skill.yaml inválido: {exc})", fg=typer.colors.RED)


# --- version ---------------------------------------------------------------


@app.command()
def version(name: str = typer.Argument(..., help="Nome da skill.")):
    """Mostra a versão atual de uma skill."""
    root = _root()
    typer.echo(core.load_skill_meta(root, name).version)


# --- bump ------------------------------------------------------------------


@app.command()
def bump(
    name: str = typer.Argument(..., help="Nome da skill."),
    part: str = typer.Argument(..., help="major | minor | patch"),
):
    """Sobe a versão da skill e adiciona uma entrada no CHANGELOG."""
    root = _root()
    meta = core.load_skill_meta(root, name)
    old = meta.version
    new = core.bump_version(old, part)
    meta.version = new
    core.save_skill_meta(root, meta)

    changelog = core.skill_path(root, name) / "CHANGELOG.md"
    if changelog.is_file():
        content = changelog.read_text(encoding="utf-8")
        entry = f"\n## [{new}]\n### Changed\n- TODO: descreva a mudança.\n"
        lines = content.splitlines(keepends=True)
        # insere após o cabeçalho (primeira linha em branco após o título)
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if i > 0 and line.startswith("## ["):
                insert_at = i
                break
        lines.insert(insert_at, entry)
        changelog.write_text("".join(lines), encoding="utf-8")

    typer.secho(f"{name}: {old} -> {new}", fg=typer.colors.GREEN)


# --- registry --------------------------------------------------------------


@app.command()
def registry():
    """Regenera registry/registry.json a partir das skills."""
    root = _root()
    path = core.write_registry(root)
    typer.secho(f"registry atualizado: {path.relative_to(root)}", fg=typer.colors.GREEN)


# --- build -----------------------------------------------------------------


@app.command()
def build():
    """Monta o plugin (plugins/vec-skills/) consumido pelo marketplace nativo."""
    root = _root()
    dest = core.build_plugin(root)
    typer.secho(f"plugin montado em {dest.relative_to(root)}", fg=typer.colors.GREEN)


@app.command()
def catalog():
    """Gera o catálogo web (docs/catalog.html) a partir do registry."""
    root = _root()
    path = core.build_catalog(root)
    typer.secho(f"catálogo gerado: {path.relative_to(root)}", fg=typer.colors.GREEN)


# --- publish ---------------------------------------------------------------


@app.command()
def publish(
    name: str = typer.Argument(..., help="Skill a publicar."),
    part: str = typer.Option(
        None, "--bump", help="Sobe a versão antes de publicar (major|minor|patch)."
    ),
    message: str = typer.Option(None, "-m", "--message", help="Mensagem do commit."),
    push: bool = typer.Option(True, help="Fazer git push."),
    release: bool = typer.Option(
        True, help="Criar tag e GitHub Release (requer gh autenticado)."
    ),
    dry_run: bool = typer.Option(False, help="Só mostra o que faria, sem alterar git."),
):
    """Valida, atualiza registry/plugin e faz commit/push/tag/release da skill."""
    root = _root()

    errors = core.validate_skill(root, name)
    if errors:
        typer.secho(f"[X] {name} inválida — corrija antes de publicar:", fg=typer.colors.RED)
        for e in errors:
            typer.echo(f"    - {e}")
        raise typer.Exit(1)

    if part:
        old = core.load_skill_meta(root, name).version
        new = core.bump_version(old, part)
        if not dry_run:
            m = core.load_skill_meta(root, name)
            m.version = new
            core.save_skill_meta(root, m)
        typer.secho(f"bump: {old} -> {new}", fg=typer.colors.CYAN)

    meta = core.load_skill_meta(root, name)
    tag = core.skill_tag(name, meta.version)
    commit_msg = message or f"skill({name}): publica v{meta.version}"

    if dry_run:
        typer.secho("[dry-run] regeneraria registry + plugin", fg=typer.colors.YELLOW)
        typer.secho(f"[dry-run] git add -A && git commit -m '{commit_msg}'", fg=typer.colors.YELLOW)
        if push:
            typer.secho("[dry-run] git push", fg=typer.colors.YELLOW)
        if release:
            typer.secho(f"[dry-run] git tag {tag} && gh release create {tag}", fg=typer.colors.YELLOW)
        return

    # 1) Commita a FONTE da skill primeiro (para o pull --rebase abaixo poder rodar).
    if core.git_has_changes(root):
        core.git(root, "add", "-A")
        core.git(root, "commit", "-m", commit_msg)
        typer.secho(f"commit: {commit_msg}", fg=typer.colors.GREEN)
    else:
        typer.secho("Nada mudou para commitar.", fg=typer.colors.YELLOW)

    # 2) Sincroniza com o remoto ANTES de regenerar — assim o build inclui as skills
    #    de outros autores (evita dropar do plugin skills que só existem no remoto).
    if push:
        try:
            core.git(root, "pull", "--rebase")
            typer.secho("sincronizado com o remoto (git pull --rebase)", fg=typer.colors.CYAN)
        except core.GitError as exc:
            typer.secho(
                f"git pull --rebase falhou — resolva o conflito e rode de novo:\n{exc}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

    # 3) Regenera catálogo/registry/plugin com o conjunto COMPLETO de skills.
    core.write_registry(root)
    core.build_plugin(root)
    core.build_catalog(root)
    if core.git_has_changes(root):
        core.git(root, "add", "-A")
        core.git(root, "commit", "-m", "chore(skillhub): regenera registry/plugin/catalogo")
        typer.secho("regenerado registry + plugin + catálogo", fg=typer.colors.GREEN)

    # 4) Publica.
    if push:
        core.git(root, "push")
        typer.secho("push feito", fg=typer.colors.GREEN)

    if release:
        if core.tag_exists(root, tag):
            typer.secho(f"tag {tag} já existe — pulando release.", fg=typer.colors.YELLOW)
        else:
            core.git(root, "tag", tag)
            if push:
                core.git(root, "push", "origin", tag)
            import shutil as _shutil
            import subprocess

            if _shutil.which("gh"):
                rel = subprocess.run(
                    ["gh", "release", "create", tag, "-t", tag, "-n", f"{name} v{meta.version}"],
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                )
                if rel.returncode == 0:
                    typer.secho(f"release {tag} criado", fg=typer.colors.GREEN)
                else:
                    typer.secho(
                        f"tag {tag} criada; 'gh release' falhou: {rel.stderr.strip()}",
                        fg=typer.colors.YELLOW,
                    )
            else:
                typer.secho(f"tag {tag} criada (gh não instalado — sem release).", fg=typer.colors.YELLOW)

    typer.secho(f"\n{name} v{meta.version} publicada.", fg=typer.colors.GREEN, bold=True)


if __name__ == "__main__":
    app()
