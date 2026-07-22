"""Núcleo do SkillHub: paths, metadados, validação, registry, build e git.

Sem estado global além da descoberta da raiz do repositório. Tudo aqui é
reutilizável pela CLI (skillhub/cli.py) e pelo GitHub Actions.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# --- Constantes do projeto -------------------------------------------------

MARKETPLACE_NAME = "vec"
PLUGIN_NAME = "vec-skills"

# "Epoch" (major) da versão do plugin. A versão é derivada da soma das skills
# (ver compute_plugin_version), o que é monotônico enquanto só ADICIONAMOS ou
# versionamos skills. Se um dia REMOVERMOS/renomearmos skills e a soma cair
# abaixo da versão já publicada, incremente este epoch para garantir que a nova
# versão continue MAIOR que a instalada (senão o app não detecta o update).
PLUGIN_VERSION_EPOCH = 2

VALID_STATUS = {"draft", "beta", "production", "deprecated"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

BUMP_PARTS = ("major", "minor", "patch")


# --- Descoberta da raiz do repositório -------------------------------------


def find_repo_root(start: Path | None = None) -> Path:
    """Sobe a árvore procurando o diretório `skills/` ao lado de `pyproject.toml`.

    Assim `skill` funciona de qualquer subpasta do repositório.
    """
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "skills").is_dir() and (candidate / "pyproject.toml").is_file():
            return candidate
    # fallback: raiz do pacote instalado em modo editável
    pkg_root = Path(__file__).resolve().parent.parent
    if (pkg_root / "skills").is_dir():
        return pkg_root
    raise FileNotFoundError(
        "Não encontrei a raiz do repositório claude-skills (procuro por skills/ + pyproject.toml). "
        "Rode o comando de dentro do repositório."
    )


def skills_dir(root: Path) -> Path:
    return root / "skills"


def registry_path(root: Path) -> Path:
    return root / "registry" / "registry.json"


# --- Modelo de uma skill ---------------------------------------------------


@dataclass
class SkillMeta:
    name: str
    version: str
    owner: str
    status: str
    description: str = ""
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "SkillMeta":
        return cls(
            name=str(data.get("name", "")),
            version=str(data.get("version", "")),
            owner=str(data.get("owner", "")),
            status=str(data.get("status", "")),
            description=str(data.get("description", "")),
            tags=list(data.get("tags", []) or []),
        )

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "version": self.version,
            "owner": self.owner,
            "status": self.status,
        }
        if self.description:
            d["description"] = self.description
        if self.tags:
            d["tags"] = self.tags
        return d


def skill_path(root: Path, name: str) -> Path:
    return skills_dir(root) / name


def load_skill_meta(root: Path, name: str) -> SkillMeta:
    yaml_file = skill_path(root, name) / "skill.yaml"
    if not yaml_file.is_file():
        raise FileNotFoundError(f"skill.yaml não encontrado para '{name}': {yaml_file}")
    data = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
    return SkillMeta.from_dict(data)


def save_skill_meta(root: Path, meta: SkillMeta) -> None:
    yaml_file = skill_path(root, meta.name) / "skill.yaml"
    yaml_file.write_text(
        yaml.safe_dump(meta.to_dict(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def list_skill_names(root: Path) -> list[str]:
    base = skills_dir(root)
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith("."))


# --- Frontmatter do SKILL.md ----------------------------------------------


def parse_frontmatter(text: str) -> dict:
    """Extrai o bloco YAML entre os primeiros dois `---` de um SKILL.md."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


# --- Semver ----------------------------------------------------------------


def bump_version(version: str, part: str) -> str:
    if not SEMVER_RE.match(version):
        raise ValueError(f"Versão inválida '{version}' (esperado X.Y.Z).")
    if part not in BUMP_PARTS:
        raise ValueError(f"Parte inválida '{part}' (use: {', '.join(BUMP_PARTS)}).")
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


# --- Validação -------------------------------------------------------------


def validate_skill(root: Path, name: str) -> list[str]:
    """Retorna lista de erros; vazia = skill válida."""
    errors: list[str] = []
    sp = skill_path(root, name)

    if not SKILL_NAME_RE.match(name):
        errors.append(f"nome '{name}' inválido (use minúsculas, números e hífen).")

    if not sp.is_dir():
        errors.append(f"pasta da skill não existe: {sp}")
        return errors

    # SKILL.md
    skill_md = sp / "SKILL.md"
    if not skill_md.is_file():
        errors.append("falta SKILL.md")
    else:
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if not fm:
            errors.append("SKILL.md sem frontmatter YAML (--- name / description ---)")
        else:
            if fm.get("name") != name:
                errors.append(
                    f"frontmatter name='{fm.get('name')}' difere da pasta '{name}'"
                )
            if not str(fm.get("description", "")).strip():
                errors.append("frontmatter sem 'description'")

    # skill.yaml
    yaml_file = sp / "skill.yaml"
    if not yaml_file.is_file():
        errors.append("falta skill.yaml")
    else:
        try:
            meta = load_skill_meta(root, name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"skill.yaml ilegível: {exc}")
        else:
            if meta.name != name:
                errors.append(f"skill.yaml name='{meta.name}' difere da pasta '{name}'")
            if not SEMVER_RE.match(meta.version):
                errors.append(f"version '{meta.version}' inválida (X.Y.Z)")
            if not meta.owner:
                errors.append("skill.yaml sem 'owner'")
            if meta.status not in VALID_STATUS:
                errors.append(
                    f"status '{meta.status}' inválido (use: {', '.join(sorted(VALID_STATUS))})"
                )

    # CHANGELOG.md
    if not (sp / "CHANGELOG.md").is_file():
        errors.append("falta CHANGELOG.md")

    # tests/
    if not (sp / "tests").is_dir():
        errors.append("falta pasta tests/")

    return errors


def validate_all(root: Path) -> dict[str, list[str]]:
    return {name: validate_skill(root, name) for name in list_skill_names(root)}


# --- Registry --------------------------------------------------------------


def build_registry(root: Path) -> dict:
    skills = []
    for name in list_skill_names(root):
        try:
            meta = load_skill_meta(root, name)
        except Exception:  # noqa: BLE001
            continue
        entry = meta.to_dict()
        entry["path"] = f"skills/{name}"
        skills.append(entry)
    return {
        "marketplace": MARKETPLACE_NAME,
        "plugin": PLUGIN_NAME,
        "generated_by": "skillhub",
        "skills": skills,
    }


def write_registry(root: Path) -> Path:
    reg = build_registry(root)
    path = registry_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


# --- Build do plugin (ponte para o marketplace nativo) ---------------------


def _plugin_skills_dir(root: Path) -> Path:
    return root / "plugins" / PLUGIN_NAME / "skills"


def compute_plugin_version(root: Path) -> str:
    """Versão do plugin derivada das skills, monotônica sob adição/bump.

    O app desktop do Claude usa o campo `version` do plugin.json para decidir se
    há atualização. Sem uma versão que CRESCE a cada mudança, o botão "Atualizar"
    nunca é habilitado. Somamos um score de cada skill (major*10000+minor*100+patch)
    de modo que adicionar uma skill nova ou versionar uma existente sempre aumenta
    o total — e portanto a versão do plugin.
    """
    total = 0
    for name in list_skill_names(root):
        try:
            meta = load_skill_meta(root, name)
        except Exception:  # noqa: BLE001
            continue
        if SEMVER_RE.match(meta.version):
            major, minor, patch = (int(x) for x in meta.version.split("."))
            total += major * 10000 + minor * 100 + patch
    return f"{PLUGIN_VERSION_EPOCH}.0.{total}"


def ensure_plugin_manifests(root: Path) -> None:
    """Grava marketplace.json e plugin.json (este com `version` para o app desktop detectar update)."""
    version = compute_plugin_version(root)

    mp = root / ".claude-plugin" / "marketplace.json"
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(
        json.dumps(
            {
                "name": MARKETPLACE_NAME,
                "owner": {"name": "VEC"},
                "plugins": [
                    {"name": PLUGIN_NAME, "source": f"./plugins/{PLUGIN_NAME}", "version": version}
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    pj = root / "plugins" / PLUGIN_NAME / ".claude-plugin" / "plugin.json"
    pj.parent.mkdir(parents=True, exist_ok=True)
    pj.write_text(
        json.dumps(
            {
                "name": PLUGIN_NAME,
                "description": "Skills compartilhadas da VEC (gerado pelo SkillHub).",
                "version": version,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def build_plugin(root: Path) -> Path:
    """Copia skills/<name>/SKILL.md (+ recursos) para plugins/vec-skills/skills/<name>/.

    É essa pasta que o marketplace nativo do Claude Code serve.
    """
    import shutil

    ensure_plugin_manifests(root)
    dest_base = _plugin_skills_dir(root)
    if dest_base.exists():
        shutil.rmtree(dest_base)
    dest_base.mkdir(parents=True, exist_ok=True)

    for name in list_skill_names(root):
        src = skill_path(root, name)
        dest = dest_base / name
        dest.mkdir(parents=True, exist_ok=True)
        # SKILL.md é obrigatório para o Claude reconhecer a skill
        skill_md = src / "SKILL.md"
        if skill_md.is_file():
            shutil.copy2(skill_md, dest / "SKILL.md")
        # copia recursos auxiliares (references/, scripts/, assets/), exceto metadados internos
        for item in src.iterdir():
            if item.name in {"SKILL.md", "skill.yaml", "CHANGELOG.md", "tests"}:
                continue
            if item.is_dir():
                shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest / item.name)
    return dest_base


# --- Catálogo web (gerado do registry) -------------------------------------

CATALOG_TEMPLATE = """<title>SkillHub — Catalog</title>
<style>
  :root {
    --bg:#F6F7F9; --surface:#FFFFFF; --ink:#16212B; --muted:#5B6773; --border:#DBE1E7;
    --teal:#0E8C86; --teal-strong:#0B6B66; --teal-wash:#E2F1F0; --amber:#B76F17;
    --amber-wash:#F6ECDC; --green:#2E8B57; --green-wash:#E4F2EA; --red:#B23B3B; --red-wash:#F6E4E4;
    --grey-wash:#EDF1F4;
    --fd:ui-sans-serif,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --fm:ui-monospace,"Cascadia Code","SFMono-Regular",Consolas,monospace;
  }
  @media (prefers-color-scheme:dark){:root{
    --bg:#0C1319; --surface:#131E28; --ink:#E7ECF1; --muted:#93A1AD; --border:#253340;
    --teal:#35B4AD; --teal-strong:#7FD6D0; --teal-wash:#142B2C; --amber:#E0A24B;
    --amber-wash:#2B2115; --green:#5FBE86; --green-wash:#14271C; --red:#E07A7A; --red-wash:#2B1616;
    --grey-wash:#1A2731;
  }}
  :root[data-theme="light"]{--bg:#F6F7F9;--surface:#FFFFFF;--ink:#16212B;--muted:#5B6773;--border:#DBE1E7;--teal:#0E8C86;--teal-strong:#0B6B66;--teal-wash:#E2F1F0;--amber:#B76F17;--amber-wash:#F6ECDC;--green:#2E8B57;--green-wash:#E4F2EA;--red:#B23B3B;--red-wash:#F6E4E4;--grey-wash:#EDF1F4;}
  :root[data-theme="dark"]{--bg:#0C1319;--surface:#131E28;--ink:#E7ECF1;--muted:#93A1AD;--border:#253340;--teal:#35B4AD;--teal-strong:#7FD6D0;--teal-wash:#142B2C;--amber:#E0A24B;--amber-wash:#2B2115;--green:#5FBE86;--green-wash:#14271C;--red:#E07A7A;--red-wash:#2B1616;--grey-wash:#1A2731;}
  *{box-sizing:border-box;}
  .page{background:var(--bg);color:var(--ink);font-family:var(--fd);line-height:1.6;-webkit-font-smoothing:antialiased;padding:clamp(20px,5vw,56px) clamp(16px,5vw,40px) 64px;}
  .wrap{max-width:1080px;margin:0 auto;}
  .eyebrow{font-family:var(--fm);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--teal-strong);display:inline-flex;align-items:center;gap:8px;}
  .eyebrow::before{content:"";width:22px;height:2px;background:var(--teal);display:inline-block;}
  h1{font-family:var(--fd);font-weight:800;letter-spacing:-.03em;font-size:clamp(32px,6vw,52px);margin:16px 0 0;}
  h1 .hub{color:var(--teal);}
  .lede{font-family:var(--fm);font-size:13px;color:var(--muted);margin:12px 0 0;}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin-top:36px;}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:22px;display:flex;flex-direction:column;gap:10px;}
  .card-top{display:flex;align-items:baseline;justify-content:space-between;gap:10px;}
  .name{font-family:var(--fm);font-size:17px;font-weight:600;margin:0;color:var(--ink);word-break:break-all;}
  .ver{font-family:var(--fm);font-size:12px;color:var(--teal-strong);background:var(--teal-wash);border:1px solid var(--teal);border-radius:999px;padding:2px 8px;white-space:nowrap;}
  .desc{margin:0;font-size:14.5px;color:var(--muted);flex:1;}
  .meta{display:flex;align-items:center;gap:10px;}
  .pill{font-family:var(--fm);font-size:11px;letter-spacing:.04em;text-transform:uppercase;padding:3px 9px;border-radius:999px;border:1px solid;}
  .pill.prod{background:var(--green-wash);color:var(--green);border-color:var(--green);}
  .pill.beta{background:var(--amber-wash);color:var(--amber);border-color:var(--amber);}
  .pill.draft{background:var(--grey-wash);color:var(--muted);border-color:var(--border);}
  .pill.dep{background:var(--red-wash);color:var(--red);border-color:var(--red);}
  .owner{font-family:var(--fm);font-size:12px;color:var(--muted);}
  .tags{display:flex;flex-wrap:wrap;gap:6px;}
  .tag{font-family:var(--fm);font-size:11px;color:var(--muted);background:var(--grey-wash);border:1px solid var(--border);border-radius:6px;padding:2px 7px;}
  .empty{color:var(--muted);}
  .foot{margin-top:48px;padding-top:22px;border-top:1px solid var(--border);font-family:var(--fm);font-size:12px;color:var(--muted);}
  .foot a{color:var(--teal);text-decoration:none;}
</style>
<div class="page"><div class="wrap">
  <header>
    <span class="eyebrow">VEC · Claude · SkillHub</span>
    <h1>Skill<span class="hub">Hub</span> catalog</h1>
    <p class="lede">__COUNT__ shared skills · plugin __PLUGIN_VERSION__ · auto-generated from the registry</p>
  </header>
  <div class="grid">
__CARDS__
  </div>
  <footer class="foot">github.com/<a href="https://github.com/rafaelnetovec/claude-skills">rafaelnetovec/claude-skills</a> · type <code>/&lt;name&gt;</code> in Claude to use a skill</footer>
</div></div>
"""


def build_catalog(root: Path) -> Path:
    """Gera docs/catalog.html a partir do registry (determinístico, sem timestamps)."""
    import html as _html

    reg = build_registry(root)
    skills = sorted(reg.get("skills", []), key=lambda x: x.get("name", ""))
    status_cls = {"production": "prod", "beta": "beta", "draft": "draft", "deprecated": "dep"}

    cards = []
    for s in skills:
        name = _html.escape(str(s.get("name", "")))
        version = _html.escape(str(s.get("version", "")))
        owner = _html.escape(str(s.get("owner", "")))
        status = str(s.get("status", "draft"))
        desc = _html.escape(str(s.get("description", "")))
        tags = "".join(
            f'<span class="tag">{_html.escape(str(t))}</span>' for t in (s.get("tags") or [])
        )
        cls = status_cls.get(status, "draft")
        cards.append(
            f'    <article class="card">\n'
            f'      <div class="card-top"><h2 class="name">/{name}</h2>'
            f'<span class="ver">v{version}</span></div>\n'
            f'      <p class="desc">{desc}</p>\n'
            f'      <div class="meta"><span class="pill {cls}">{_html.escape(status)}</span>'
            f'<span class="owner">{owner}</span></div>\n'
            f'      <div class="tags">{tags}</div>\n'
            f'    </article>'
        )

    cards_html = "\n".join(cards) if cards else '    <p class="empty">No skills yet.</p>'
    doc = (
        CATALOG_TEMPLATE
        .replace("__COUNT__", str(len(skills)))
        .replace("__PLUGIN_VERSION__", compute_plugin_version(root))
        .replace("__CARDS__", cards_html)
    )
    out = root / "docs" / "catalog.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


# --- Git -------------------------------------------------------------------


class GitError(RuntimeError):
    pass


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise GitError(
            f"git {' '.join(args)} falhou (código {result.returncode}):\n{result.stderr.strip()}"
        )
    return result


def git_has_changes(root: Path) -> bool:
    return bool(git(root, "status", "--porcelain").stdout.strip())


def tag_exists(root: Path, tag: str) -> bool:
    res = git(root, "tag", "--list", tag)
    return bool(res.stdout.strip())


def skill_tag(name: str, version: str) -> str:
    return f"{name}-v{version}"
