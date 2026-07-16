# SkillHub — gerenciador de skills do Claude Code da VEC

Fonte única da verdade para as skills compartilhadas do time. Cada skill é
versionada (semver), validada automaticamente e distribuída pelo **plugin
marketplace nativo** do Claude Code (auto-update por *pull*).

## Estrutura

```
claude-skills/
├── skills/                    # fonte da verdade (uma pasta por skill)
│   └── exemplo-vec/
│       ├── SKILL.md           # a skill em si (frontmatter name/description)
│       ├── skill.yaml         # metadados: name, version, owner, status
│       ├── CHANGELOG.md
│       └── tests/
├── registry/
│   └── registry.json          # catálogo gerado (skill registry)
├── skillhub/                  # a CLI `skill` (Python/Typer)
├── plugins/vec-skills/        # plugin gerado (o que o marketplace serve)
├── .claude-plugin/            # marketplace.json (gerado)
├── .github/workflows/         # CI: valida + sincroniza + release
└── pyproject.toml
```

> Nota: a proposta original citava `CLAUDE.md` como arquivo da skill. O Claude Code
> carrega skills a partir de **`SKILL.md`** (com frontmatter), então esse é o
> arquivo usado aqui. O `skill.yaml` guarda os metadados/semver ao lado.

## Instalar a CLI

```powershell
cd claude-skills
python -m pip install -e .
```

Depois o comando `skill` fica disponível no terminal.

## Comandos (V1)

| Comando | O que faz |
|---|---|
| `skill create <nome>` | Cria o esqueleto da skill (SKILL.md, skill.yaml, CHANGELOG.md, tests/). |
| `skill validate [nome]` | Valida estrutura e metadados (sem nome = todas). |
| `skill list` | Lista skills com versão, owner e status. |
| `skill version <nome>` | Mostra a versão atual. |
| `skill bump <nome> <major\|minor\|patch>` | Sobe a versão e registra no CHANGELOG. |
| `skill registry` | Regenera `registry/registry.json`. |
| `skill build` | Monta `plugins/vec-skills/` (o que o marketplace serve). |
| `skill publish <nome>` | Valida → (bump opcional) → registry → build → commit/push/tag/release. |

Exemplos:

```powershell
skill create planner --owner growth
skill validate planner
skill bump planner minor
skill publish planner --bump patch      # sobe patch, commita, push, tag + release
skill publish planner --dry-run         # mostra o que faria, sem tocar no git
```

## Distribuição para o time (instalação = plugin inteiro)

O consumo continua pelo marketplace nativo do Claude Code. Cada pessoa cadastra
o marketplace `vec` uma única vez (com `autoUpdate: true`); ao abrir o Claude, o
plugin `vec-skills` é atualizado automaticamente com a última versão da `main`.

## CI (GitHub Actions)

- **Pull request** → roda `skill validate` (bloqueia merge se algo estiver inválido).
- **Push na `main`** → regenera `registry.json` + monta o plugin, commita a
  sincronização e cria uma **tag + release por skill** (`<nome>-v<versão>`).

Ninguém precisa lembrar de atualizar o registry ou criar releases à mão.

## Roadmap

- **V2:** `skill install`, `skill uninstall`, `skill update [--all]` como atalhos
  do `claude plugin`; `skill run` para exercitar os testes de fumaça.
- **V3:** `skill doctor` e sincronização com as Claude Skills do app (via API se
  existir, ou automação de interface).
