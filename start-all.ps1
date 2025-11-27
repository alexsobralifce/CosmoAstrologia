# Script PowerShell para iniciar frontend e backend simultaneamente
# Uso: .\start-all.ps1

# Obter o diretório do script (raiz do projeto)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "🚀 Iniciando Astrologia (Frontend + Backend)..." -ForegroundColor Cyan
Write-Host ""

# Matar processos antigos nas portas
Write-Host "🧹 Limpando processos antigos..." -ForegroundColor Yellow
$backendProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
$frontendProcess = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($backendProcess) { Stop-Process -Id $backendProcess -Force -ErrorAction SilentlyContinue }
if ($frontendProcess) { Stop-Process -Id $frontendProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1

# Iniciar backend
Write-Host "📦 Iniciando backend..." -ForegroundColor Cyan
$backendScript = @"
cd '$ScriptDir\backend'
if (-not (Test-Path venv)) { 
    python -m venv venv 
}
.\venv\Scripts\Activate.ps1
if (-not (python -c 'import fastapi' 2>`$null)) { 
    pip install -r requirements.txt 
}
if (-not (Test-Path astrologia.db)) { 
    python -c 'from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)' 
}
python run.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal

# Aguardar backend iniciar
Write-Host "⏳ Aguardando backend iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar se backend está rodando
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend iniciado!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend pode não estar rodando ainda. Verifique a janela do backend." -ForegroundColor Yellow
}

# Iniciar frontend
Write-Host "🎨 Iniciando frontend..." -ForegroundColor Cyan
$frontendScript = @"
cd '$ScriptDir'
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

# Aguardar frontend iniciar
Write-Host "⏳ Aguardando frontend iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ Servidores iniciados em janelas separadas!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Feche as janelas do PowerShell para parar os servidores" -ForegroundColor Yellow
Write-Host ""

