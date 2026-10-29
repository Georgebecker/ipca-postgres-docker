# instalar.ps1 - ativa os ganchos de protecao do git neste projeto
# Uso: powershell -ExecutionPolicy Bypass -File .githooks\instalar.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    if (-not (Test-Path ".git")) {
        Write-Host "Nenhum repositorio git aqui. Inicializando 'git init'..."
        git init
    }
    git config core.hooksPath .githooks
    foreach ($gancho in "pre-commit", "commit-msg", "pre-push") {
        if (-not (Test-Path ".githooks\$gancho")) { throw "Gancho ausente: .githooks\$gancho" }
    }
    Write-Host ""
    Write-Host "Protecao ativa em tres momentos: commit, mensagem e envio ao remoto."
    Write-Host "  - no commit:    arquivo .githooks\pre-commit  (segredo e chave)"
    Write-Host "  - na mensagem:  arquivo .githooks\commit-msg  (coautoria de IA)"
    Write-Host "  - no envio:     arquivo .githooks\pre-push    (as duas regras de novo)"
    Write-Host "Nenhum arquivo com valor de chave entra no git de jeito nenhum,"
    Write-Host "e nenhum modelo de IA aparece como autor ou contribuidor."
} finally {
    Pop-Location
}
