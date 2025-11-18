# Script PowerShell para iniciar/parar frontend e backend do sistema de Astrologia
# Uso: .\start.ps1

$FRONTEND_PORT = 3000
$BACKEND_PORT = 8000
$FRONTEND_PID_FILE = ".frontend.pid"
$BACKEND_PID_FILE = ".backend.pid"

# Função para encontrar PID por porta
function Get-ProcessByPort {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
    if ($connection) {
        return $connection.OwningProcess
    }
    return $null
}

# Verificar se frontend está rodando
$frontendRunning = $false
$frontendPid = Get-ProcessByPort -Port $FRONTEND_PORT
if ($frontendPid) {
    $frontendRunning = $true
}

# Verificar se backend está rodando
$backendRunning = $false
$backendPid = Get-ProcessByPort -Port $BACKEND_PORT
if ($backendPid) {
    $backendRunning = $true
}

# Se ambos estiverem rodando, matar os processos
if ($frontendRunning -or $backendRunning) {
    Write-Host "=== Encerrando serviços ===" -ForegroundColor Blue
    
    if ($frontendRunning) {
        Write-Host "Matando processo Frontend (PID: $frontendPid)..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $frontendPid -Force -ErrorAction Stop
            Write-Host "Processo Frontend encerrado" -ForegroundColor Green
        } catch {
            Write-Host "Erro ao encerrar Frontend: $_" -ForegroundColor Red
        }
        if (Test-Path $FRONTEND_PID_FILE) { Remove-Item $FRONTEND_PID_FILE }
    }
    
    if ($backendRunning) {
        Write-Host "Matando processo Backend (PID: $backendPid)..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $backendPid -Force -ErrorAction Stop
            Write-Host "Processo Backend encerrado" -ForegroundColor Green
        } catch {
            Write-Host "Erro ao encerrar Backend: $_" -ForegroundColor Red
        }
        if (Test-Path $BACKEND_PID_FILE) { Remove-Item $BACKEND_PID_FILE }
    }
    
    Write-Host "Serviços encerrados!" -ForegroundColor Green
    exit 0
}

# Se não estiverem rodando, iniciar ambos
Write-Host "=== Iniciando serviços ===" -ForegroundColor Blue

# Verificar se estamos na raiz do projeto
if (-not (Test-Path "package.json") -or -not (Test-Path "backend")) {
    Write-Host "Erro: Execute este script na raiz do projeto" -ForegroundColor Red
    exit 1
}

# Função para limpar ao sair
function Cleanup {
    Write-Host "`n=== Encerrando serviços ===" -ForegroundColor Yellow
    if (Test-Path $FRONTEND_PID_FILE) {
        $pid = Get-Content $FRONTEND_PID_FILE
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Remove-Item $FRONTEND_PID_FILE
    }
    if (Test-Path $BACKEND_PID_FILE) {
        $pid = Get-Content $BACKEND_PID_FILE
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Remove-Item $BACKEND_PID_FILE
    }
}

# Capturar Ctrl+C para limpar processos
[Console]::TreatControlCAsInput = $false
$null = Register-ObjectEvent -InputObject ([System.Console]) -EventName "CancelKeyPress" -Action {
    Cleanup
    exit 0
}

# Iniciar Backend
Write-Host "Iniciando Backend na porta $BACKEND_PORT..." -ForegroundColor Blue
Push-Location backend

# Verificar se existe venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

# Iniciar backend em background
$backendProcess = Start-Process -FilePath "python" -ArgumentList "run.py" -RedirectStandardOutput "..\.backend.log" -RedirectStandardError "..\.backend.log" -PassThru -NoNewWindow
$backendPid = $backendProcess.Id
$backendPid | Out-File "..\$BACKEND_PID_FILE"

Pop-Location

Write-Host "Backend iniciado - PID: $backendPid" -ForegroundColor Green
Write-Host "Logs do Backend: Get-Content .backend.log -Wait" -ForegroundColor Blue
Write-Host ""

# Aguardar backend iniciar
Write-Host "Aguardando backend iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verificar se backend está rodando
if (-not (Get-Process -Id $backendPid -ErrorAction SilentlyContinue)) {
    Write-Host "Erro: Backend não iniciou corretamente" -ForegroundColor Red
    Write-Host "Verifique os logs: Get-Content .backend.log" -ForegroundColor Yellow
    Remove-Item $BACKEND_PID_FILE -ErrorAction SilentlyContinue
    exit 1
}

# Verificar se node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependências do frontend..." -ForegroundColor Yellow
    npm install
}

# Iniciar Frontend
Write-Host "Iniciando Frontend na porta $FRONTEND_PORT..." -ForegroundColor Blue

# Iniciar frontend em background
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -RedirectStandardOutput ".frontend.log" -RedirectStandardError ".frontend.log" -PassThru -NoNewWindow
$frontendPid = $frontendProcess.Id
$frontendPid | Out-File $FRONTEND_PID_FILE

Write-Host "Frontend iniciado - PID: $frontendPid" -ForegroundColor Green
Write-Host "Logs do Frontend: Get-Content .frontend.log -Wait" -ForegroundColor Blue
Write-Host ""

# Aguardar frontend iniciar
Write-Host "Aguardando frontend iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verificar se frontend está rodando
if (-not (Get-Process -Id $frontendPid -ErrorAction SilentlyContinue)) {
    Write-Host "Erro: Frontend não iniciou corretamente" -ForegroundColor Red
    Write-Host "Verifique os logs: Get-Content .frontend.log" -ForegroundColor Yellow
    Remove-Item $FRONTEND_PID_FILE -ErrorAction SilentlyContinue
    Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
    Remove-Item $BACKEND_PID_FILE -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  ✅ Serviços iniciados com sucesso!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:$FRONTEND_PORT (PID: $frontendPid)" -ForegroundColor Blue
Write-Host "Backend:  http://localhost:$BACKEND_PORT (PID: $backendPid)" -ForegroundColor Blue
Write-Host ""
Write-Host "Ver logs em tempo real:" -ForegroundColor Yellow
Write-Host "  Backend:  Get-Content .backend.log -Wait" -ForegroundColor Blue
Write-Host "  Frontend: Get-Content .frontend.log -Wait" -ForegroundColor Blue
Write-Host ""
Write-Host "Pressione Ctrl+C para encerrar os serviços" -ForegroundColor Yellow
Write-Host ""

# Aguardar até que os processos terminem
try {
    Wait-Process -Id $backendPid, $frontendPid
} catch {
    # Processos foram encerrados
}

# Limpar ao sair
Cleanup

