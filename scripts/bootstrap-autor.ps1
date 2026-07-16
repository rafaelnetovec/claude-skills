# bootstrap-autor.ps1 - prepara a maquina de um AUTOR para criar/publicar skills da VEC.
#
# Uso:
#   # se voce ja clonou o repo, rode de dentro dele:
#   ./scripts/bootstrap-autor.ps1
#   # ou standalone (ele clona pra voce):
#   ./bootstrap-autor.ps1
#
# Idempotente: pode rodar de novo sem problema.
# NAO resolve: acesso de escrita (voce precisa ser colaborador com Write) nem o login
# do git — essas partes exigem acao humana; o script avisa se faltarem.

param(
    [string]$Repo = "rafaelnetovec/claude-skills",
    [string]$TargetDir = (Join-Path $env:USERPROFILE "claude-skills")
)
$ErrorActionPreference = "Stop"

function Fail($m) { Write-Host "  [ERRO] $m" -ForegroundColor Red; exit 1 }
function Ok($m)   { Write-Host "  [ok] $m" -ForegroundColor Green }
function Info($m) { Write-Host $m -ForegroundColor Cyan }

Info "== SkillHub - bootstrap do autor =="

# 1) Pre-requisitos ---------------------------------------------------------
Info "`n1) Conferindo git e python..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail "git nao encontrado. Instale o Git." }
Ok "git encontrado"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Fail "python nao encontrado. Instale o Python 3.10+." }
$pyver = ((python --version) -replace 'Python\s*','').Trim()
$parts = $pyver.Split('.')
if ([int]$parts[0] -lt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -lt 10)) {
    Fail "Python $pyver e antigo demais. Precisa de 3.10+."
}
Ok "python $pyver"

# 2) Localizar ou clonar o repo --------------------------------------------
Info "`n2) Localizando o repositorio..."
$scriptRepo = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { $null }
if ($scriptRepo -and (Test-Path (Join-Path $scriptRepo "pyproject.toml")) -and (Test-Path (Join-Path $scriptRepo "skills"))) {
    $repoRoot = $scriptRepo
    Ok "usando o repo onde este script esta: $repoRoot"
} elseif (Test-Path (Join-Path $TargetDir ".git")) {
    $repoRoot = $TargetDir
    Ok "repo ja clonado em $repoRoot (atualizando)"
    git -C $repoRoot pull --quiet
} else {
    Info "  clonando $Repo em $TargetDir ..."
    git clone "https://github.com/$Repo.git" $TargetDir
    if ($LASTEXITCODE -ne 0) { Fail "falha ao clonar. Voce e colaborador (com Write) e o git esta autenticado nessa conta?" }
    $repoRoot = $TargetDir
    Ok "clonado em $repoRoot"
}
Set-Location $repoRoot

# 3) Instalar a CLI ---------------------------------------------------------
Info "`n3) Instalando a CLI do SkillHub..."
python -m pip install -e . --quiet
if ($LASTEXITCODE -ne 0) { Fail "falha ao instalar a CLI (python -m pip install -e .)." }
Ok "CLI instalada"

# 4) Testar acesso ao remoto (leitura + autenticacao) -----------------------
Info "`n4) Testando acesso ao repositorio remoto..."
git ls-remote origin | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "sem acesso ao remoto. Aceite o convite de colaborador e verifique a autenticacao do git." }
Ok "leitura/autenticacao do remoto confirmada (a escrita e validada no 1o publish)"

# 5) Resumo -----------------------------------------------------------------
Info "`n== Pronto! Skills atuais no repo: =="
python -m skillhub.cli list

Info "`nProximos passos (criar e publicar uma skill):"
Write-Host '  skill create my-skill --owner growth --description "What it does."'
Write-Host '  skill validate my-skill'
Write-Host '  skill bump my-skill minor'
Write-Host '  skill publish my-skill --no-release'
Write-Host ""
Write-Host "Se 'skill' nao for reconhecido, use 'python -m skillhub.cli' no lugar." -ForegroundColor DarkGray
Write-Host "Duas contas GitHub? Se o push der 403, rode:" -ForegroundColor DarkGray
Write-Host '  git remote set-url origin https://SEU-USUARIO@github.com/rafaelnetovec/claude-skills.git' -ForegroundColor DarkGray
