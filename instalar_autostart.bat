@echo off
echo Instalando Monitor PDV como tarefa de inicializacao automatica...
echo.

set "SCRIPT=%~dp0iniciar_silencioso.vbs"

REM Remove tarefa antiga se existir
schtasks /delete /tn "MonitorPDV" /f >nul 2>&1

REM Cria nova tarefa: executa no logon do usuario atual, sem janela
schtasks /create ^
  /tn "MonitorPDV" ^
  /tr "wscript.exe \"%SCRIPT%\"" ^
  /sc ONLOGON ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f

if %errorlevel% == 0 (
    echo [OK] Tarefa registrada com sucesso!
    echo.
    echo O Monitor PDV e o n8n vao iniciar automaticamente no proximo login.
    echo.
    echo Para verificar: Agendador de Tarefas ^> MonitorPDV
    echo Para remover:   desinstalar_autostart.bat
) else (
    echo [ERRO] Falha ao registrar. Tente executar como Administrador.
)
echo.
pause
