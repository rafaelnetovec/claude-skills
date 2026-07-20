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
2. **Git** e **Python 3.10+** instalados. Se a máquina não tiver, instale:

   **Windows** (PowerShell):
   ```powershell
   winget install Git.Git
   winget install Python.Python.3.12
   ```
   (ou baixe de git-scm.com e python.org — no instalador do Python, marque **"Add to PATH"**)

   **Mac** (Terminal):
   ```bash
   xcode-select --install     # instala o git (Command Line Tools)
   brew install python         # Python 3.10+  (não tem Homebrew? instale em brew.sh)
   ```

   **Feche e reabra o terminal** depois de instalar e confirme:
   - Windows: `git --version` e `python --version`
   - Mac: `git --version` e `python3 --version`

---

## Parte 1 — Preparar a máquina (uma vez)

**Onde eu rodo o `git clone`? Em que pasta?**
Abra o terminal — ele já começa na sua **pasta pessoal** (`C:\Users\voce` no Windows,
`/Users/voce` no Mac). Pode clonar ali mesmo: o `git clone` cria uma **subpasta nova**
chamada `claude-skills` dentro da pasta onde você está. Se preferir outro lugar, dê `cd`
para lá antes (ex.: `cd Documents`). Não precisa criar a pasta à mão — o clone cria.

Depois de clonar, entre nela com `cd claude-skills`. É essa a pasta onde você abre o
Claude Code para publicar skills.

> ⚠️ **Não abra o PowerShell como Administrador.** Isso o inicia em `C:\WINDOWS\System32`,
> uma pasta protegida — o clone falha com *"could not create work tree dir: Permission
> denied"*. Use um PowerShell normal e o `cd` abaixo garante uma pasta com permissão.

### Windows (PowerShell)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # libera rodar .ps1 nesta janela
cd $env:USERPROFILE                                          # vai para C:\Users\voce (pasta com permissao)
git clone https://github.com/rafaelnetovec/claude-skills.git
cd claude-skills
.\scripts\bootstrap-autor.ps1
```

### Mac (Terminal)
```bash
cd ~                                                         # sua pasta pessoal
git clone https://github.com/rafaelnetovec/claude-skills.git
cd claude-skills
bash scripts/bootstrap-autor.sh
```

O **bootstrap** confere git/python, instala a CLI e testa o acesso ao repo — e avisa
exatamente o que faltar. (Equivalente manual: `python -m pip install -e .` no Windows,
`python3 -m pip install -e .` no Mac.)

Se o comando `skill` não for reconhecido depois, use `python -m skillhub.cli` (Windows) ou
`python3 -m skillhub.cli` (Mac) no lugar de `skill`.

---

## Parte 2 — Criar e publicar uma skill

**Jeito mais fácil — só pedir ao Claude.** Com o Claude Code aberto na pasta do repo,
descreva a skill em português (ex.: *"crie uma skill que revisa notas de reunião e
publique"*). O Claude roda todo o fluxo por você — create, validate, bump, publish —
seguindo o `CLAUDE.md` do repo. Foi assim que este projeto foi construído. Os comandos
abaixo são o equivalente manual, caso prefira rodar você mesmo:

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
