@echo off
REM Script para iniciar/parar frontend e backend do sistema de Astrologia (Windows)
REM Uso: start.bat

setlocal enabledelayedexpansion

set FRONTEND_PORT=3000
set BACKEND_PORT=8000
set FRONTEND_PID_FILE=.frontend.pid
set BACKEND_PID_FILE=.backend.pid

REM Função para encontrar PID por porta
:find_pid_by_port
set PORT=%1
set PID=
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    set PID=%%a
    goto :found_pid
)
:found_pid
exit /b

REM Verificar se frontend está rodando
set FRONTEND_RUNNING=0
set FRONTEND_PID=
netstat -ano | findstr :%FRONTEND_PORT% | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    set FRONTEND_RUNNING=1
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%FRONTEND_PORT% ^| findstr LISTENING') do set FRONTEND_PID=%%a
)

REM Verificar se backend está rodando
set BACKEND_RUNNING=0
set BACKEND_PID=
netstat -ano | findstr :%BACKEND_PORT% | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    set BACKEND_RUNNING=1
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%BACKEND_PORT% ^| findstr LISTENING') do set BACKEND_PID=%%a
)

REM Se ambos estiverem rodando, matar os processos
if %FRONTEND_RUNNING% == 1 (
    echo === Encerrando Frontend (PID: !FRONTEND_PID!) ===
    taskkill /PID !FRONTEND_PID! /F >nul 2>&1
    del /f /q %FRONTEND_PID_FILE% >nul 2>&1
    echo Frontend encerrado
)

if %BACKEND_RUNNING% == 1 (
    echo === Encerrando Backend (PID: !BACKEND_PID!) ===
    taskkill /PID !BACKEND_PID! /F >nul 2>&1
    del /f /q %BACKEND_PID_FILE% >nul 2>&1
    echo Backend encerrado
)

if %FRONTEND_RUNNING% == 1 (
    echo Servicos encerrados!
    pause
    exit /b 0
)

if %BACKEND_RUNNING% == 1 (
    echo Servicos encerrados!
    pause
    exit /b 0
)

REM Se não estiverem rodando, iniciar ambos
echo === Iniciando servicos ===

REM Verificar se estamos na raiz do projeto
if not exist "package.json" (
    echo Erro: Execute este script na raiz do projeto
    pause
    exit /b 1
)

if not exist "backend" (
    echo Erro: Pasta backend nao encontrada
    pause
    exit /b 1
)

REM Iniciar Backend
echo Iniciando Backend na porta %BACKEND_PORT%...
cd backend

REM Verificar se existe venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Iniciar backend em background
start "Backend - Astrologia" /B python run.py > ..\.backend.log 2>&1

REM Obter PID do processo Python mais recente na porta 8000
timeout /t 2 /nobreak >nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%BACKEND_PORT% ^| findstr LISTENING') do (
    set BACKEND_PID=%%a
    echo !BACKEND_PID! > ..\%BACKEND_PID_FILE%
    goto :backend_started
)

:backend_started
cd ..

if defined BACKEND_PID (
    echo Backend iniciado - PID: !BACKEND_PID!
) else (
    echo ERRO: Backend nao iniciou corretamente
    echo Verifique os logs: type .backend.log
    pause
    exit /b 1
)

REM Verificar se node_modules existe
if not exist "node_modules" (
    echo Instalando dependencias do frontend...
    call npm install
)

REM Iniciar Frontend
echo Iniciando Frontend na porta %FRONTEND_PORT%...
start "Frontend - Astrologia" /B cmd /c "npm run dev > .frontend.log 2>&1"

REM Obter PID do processo Node mais recente na porta 3000
timeout /t 3 /nobreak >nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%FRONTEND_PORT% ^| findstr LISTENING') do (
    set FRONTEND_PID=%%a
    echo !FRONTEND_PID! > %FRONTEND_PID_FILE%
    goto :frontend_started
)

:frontend_started

if defined FRONTEND_PID (
    echo Frontend iniciado - PID: !FRONTEND_PID!
) else (
    echo ERRO: Frontend nao iniciou corretamente
    echo Verifique os logs: type .frontend.log
    taskkill /PID !BACKEND_PID! /F >nul 2>&1
    del /f /q %BACKEND_PID_FILE% >nul 2>&1
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Servicos iniciados com sucesso!
echo ========================================
echo.
echo Frontend: http://localhost:%FRONTEND_PORT% (PID: !FRONTEND_PID!)
echo Backend:  http://localhost:%BACKEND_PORT% (PID: !BACKEND_PID!)
echo.
echo Ver logs em tempo real:
echo   Backend:  type .backend.log
echo   Frontend: type .frontend.log
echo.
echo Os processos estao rodando em janelas separadas.
echo Feche as janelas "Backend - Astrologia" e "Frontend - Astrologia" para encerrar.
echo.
pause

