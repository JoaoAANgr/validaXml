@echo off
echo Removendo tarefa de inicializacao automatica...
schtasks /delete /tn "MonitorPDV" /f
if %errorlevel% == 0 (
    echo [OK] Tarefa removida.
) else (
    echo [AVISO] Tarefa nao encontrada ou ja removida.
)
pause
