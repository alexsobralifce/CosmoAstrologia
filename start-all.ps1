# Script PowerShell para iniciar frontend e backend simultaneamente
# Uso: .\start-all.ps1

Write-Host "🚀 Iniciando Astrologia (Frontend + Backend)..." -ForegroundColor Cyan
Write-Host ""

# Iniciar backend
Write-Host "📦 Iniciando backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; if (-not (Test-Path venv)) { python -m venv venv }; .\venv\Scripts\Activate.ps1; if (-not (python -c 'import fastapi' 2>`$null)) { pip install -r requirements.txt }; if (-not (Test-Path astrologia.db)) { python -c 'from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)' }; python run.py" -WindowStyle Normal

# Aguardar backend iniciar
Start-Sleep -Seconds 3

# Iniciar frontend
Write-Host "🎨 Iniciando frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Servidores iniciados em janelas separadas!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔧 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Feche as janelas do PowerShell para parar os servidores" -ForegroundColor Yellow

