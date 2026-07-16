# onboard.ps1 - Assina o marketplace de skills da VEC (SkillHub) nesta maquina.
#
# Uso (no PowerShell):
#   ./onboard.ps1
#
# O que faz: configura o ~/.claude/settings.json para assinar o marketplace "vec"
# e habilitar o plugin "vec-skills" com auto-update. Idempotente: pode rodar de novo.
#
# Repo PRIVADO: alem de rodar este script, defina um token do GitHub (veja o final).

param(
    [string]$Repo = "rafaelnetovec/claude-skills",   # repo central das skills (SkillHub)
    [string]$MarketplaceName = "vec",
    [string]$PluginName = "vec-skills"
)

$ErrorActionPreference = "Stop"
$settingsPath = Join-Path $env:USERPROFILE ".claude\settings.json"

# Le settings.json atual (ou comeca vazio)
if (Test-Path $settingsPath) {
    $json = Get-Content $settingsPath -Raw
    if ([string]::IsNullOrWhiteSpace($json)) { $settings = [ordered]@{} }
    else { $settings = $json | ConvertFrom-Json }
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path $settingsPath) | Out-Null
    $settings = [ordered]@{}
}

# Converte PSCustomObject para hashtable mutavel (preservando o que ja existe)
function To-Hashtable($obj) {
    $h = [ordered]@{}
    if ($null -ne $obj) {
        foreach ($p in $obj.PSObject.Properties) { $h[$p.Name] = $p.Value }
    }
    return $h
}
$settings = To-Hashtable $settings

# --- extraKnownMarketplaces (assina o repo "vec" com auto-update) ---
$markets = To-Hashtable $settings["extraKnownMarketplaces"]
$markets[$MarketplaceName] = [ordered]@{
    source     = [ordered]@{ source = "github"; repo = $Repo }
    autoUpdate = $true
}
$settings["extraKnownMarketplaces"] = $markets

# --- enabledPlugins (liga o plugin vec-skills@vec) ---
$plugins = To-Hashtable $settings["enabledPlugins"]
$plugins["$PluginName@$MarketplaceName"] = $true
$settings["enabledPlugins"] = $plugins

# Grava de volta (UTF-8 sem BOM)
$out = $settings | ConvertTo-Json -Depth 20
[System.IO.File]::WriteAllText($settingsPath, $out, [System.Text.UTF8Encoding]::new($false))

Write-Host ""
Write-Host "OK! settings.json configurado em: $settingsPath" -ForegroundColor Green
Write-Host "  Marketplace : $MarketplaceName  ->  github:$Repo (autoUpdate ligado)"
Write-Host "  Plugin      : $PluginName@$MarketplaceName habilitado"
Write-Host ""
Write-Host "Repo PRIVADO: defina um token do GitHub nesta maquina (uma vez):" -ForegroundColor Yellow
Write-Host '  setx GH_TOKEN "seu_token_de_leitura_aqui"'
Write-Host "  (feche e reabra o terminal depois do setx para o token valer)"
Write-Host ""
Write-Host "Agora FECHE e REABRA o Claude Code e peca: 'testar as skills da VEC'." -ForegroundColor Cyan
