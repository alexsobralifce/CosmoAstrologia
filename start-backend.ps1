# Script PowerShell para iniciar o backend do Astrologia
# Uso: .\start-backend.ps1

$ErrorActionPreference = "Stop"

Set-Location -Path "$PSScriptRoot\backend"

Write-Host "🚀 Iniciando backend do Astrologia..." -ForegroundColor Cyan
Write-Host ""

# Verificar se o ambiente virtual existe
if (-not (Test-Path "venv")) {
    Write-Host "❌ Ambiente virtual não encontrado. Criando..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Ambiente virtual criado!" -ForegroundColor Green
}

# Ativar ambiente virtual
Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Verificar se as dependências estão instaladas
try {
    python -c "import fastapi" 2>$null
} catch {
    Write-Host "📥 Instalando dependências..." -ForegroundColor Cyan
    pip install -r requirements.txt
    Write-Host "✅ Dependências instaladas!" -ForegroundColor Green
}

# Verificar se o banco de dados existe, se não, criar
if (-not (Test-Path "astrologia.db")) {
    Write-Host "🗄️  Criando banco de dados..." -ForegroundColor Cyan
    python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
    Write-Host "✅ Banco de dados criado!" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Backend pronto!" -ForegroundColor Green
Write-Host "🌐 Servidor rodando em: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentação da API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar o servidor
python run.py

