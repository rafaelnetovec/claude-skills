# Guia do autor — criar e publicar skills da VEC (SkillHub)

Este guia é para **quem vai criar/manter skills** (o autor). Quem só usa as skills não
precisa disto — ver o [Guia do consumidor](GUIA-CONSUMIDOR.md).

O autor trabalha com a CLI `skill`, que cuida de estrutura, versão, validação e
publicação (commit + push). O GitHub Actions faz o resto (valida, atualiza o catálogo
e cria os releases).

---

## Pré-requisitos (uma vez por pessoa)

1. **Acesso de ESCRITA** ao repositório `rafaelnetovec/claude-skills`
   (colaborador com permissão *Write*, ou membro da org quando o repo migrar).
   > Consumidor precisa só de leitura; autor precisa de escrita para dar `push`.
2. **Git** instalado.
3. **Python 3.10+** instalado (`python --version`).

---

## Parte 1 — Preparar a máquina (uma vez)

**Caminho rápido (recomendado):** rode o bootstrap, que clona, instala a CLI e confere o
acesso de uma vez:

```powershell
# se já clonou o repo, rode de dentro dele:
./scripts/bootstrap-autor.ps1
# ou standalone (ele clona pra você) — tendo o script em mãos:
./bootstrap-autor.ps1
```

**Caminho manual (equivalente):**

```powershell
# 1. Clonar o repositório
git clone https://github.com/rafaelnetovec/claude-skills.git
cd claude-skills

# 2. Instalar a CLI do SkillHub (modo editável)
python -m pip install -e .
```

Depois disso o comando fica disponível como `skill`. Se o terminal não encontrar
`skill` (a pasta de Scripts do Python pode não estar no PATH), use a forma equivalente
`python -m skillhub.cli` no lugar de `skill` em qualquer comando abaixo.

Confirme:
```powershell
python -m skillhub.cli list
```

---

## Parte 2 — Criar e publicar uma skill

```powershell
# 1. Criar o esqueleto (SKILL.md, skill.yaml, CHANGELOG.md, tests/)
skill create minha-skill --owner growth --description "O que a skill faz."

# 2. Editar o conteúdo da skill
#    Abra skills/minha-skill/SKILL.md e escreva a skill (o frontmatter name/description
#    é o que faz o Claude reconhecê-la). Ajuste o status em skill.yaml para
#    draft | beta | production conforme a maturidade.

# 3. Validar estrutura e metadados
skill validate minha-skill

# 4. (Quando mudar algo) subir a versão — semver
skill bump minha-skill minor      # 1.0.0 -> 1.1.0   (patch|minor|major)

# 5. Publicar: valida + atualiza catálogo/plugin + commit + push
skill publish minha-skill --no-release
```

O `--no-release` deixa o **GitHub Actions** criar a tag e o release (recomendado —
não depende de `gh` autenticado na sua máquina). Use `skill publish minha-skill --dry-run`
para ver o que aconteceria sem tocar no git.

O que o CI faz sozinho após o push na `main`:
- valida todas as skills;
- regenera `registry/registry.json` e o plugin `plugins/vec-skills/`;
- cria **tag + release** por skill (`minha-skill-v1.1.0`).

---

## Parte 3 — Boas práticas

- **Uma pasta por skill** em `skills/`. Nunca edite `plugins/` na mão — é gerado.
- **Versione sempre que mudar** (`skill bump`) — é o que faz o app dos consumidores
  detectar que há atualização.
- **Status**: comece em `draft`/`beta` e só marque `production` quando estiver pronta.
- **Revisão (recomendado):** em vez de `publish` direto na `main`, trabalhe num branch
  e abra um **Pull Request**. O CI valida o PR e o merge só entra se passar — melhor
  para times com vários autores.

---

## Gotchas conhecidos

- **Duas contas GitHub na mesma máquina:** se o `git push` falhar com *"denied to
  OUTRA-CONTA"* (403), o git está usando a conta errada. Aponte o remote para a conta
  certa embutindo o usuário na URL:
  ```powershell
  git remote set-url origin https://SEU-USUARIO@github.com/rafaelnetovec/claude-skills.git
  ```
- **Comando `skill` não encontrado:** use `python -m skillhub.cli ...`, ou adicione a
  pasta de Scripts do Python ao PATH.
- **Sempre `git pull` antes de começar:** vários autores = evite conflito puxando o
  mais recente antes de criar/editar.
