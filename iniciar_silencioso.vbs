' Inicia n8n e monitor em background sem abrir janelas de console
Dim shell
Set shell = CreateObject("WScript.Shell")

' Aguarda 10s para a rede e o sistema estarem prontos
WScript.Sleep 10000

' Inicia o n8n
shell.Run "cmd /c n8n start", 0, False

' Aguarda o n8n subir
WScript.Sleep 15000

' Inicia o monitor PDV
Dim pasta
pasta = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
shell.Run "cmd /c cd /d """ & pasta & """ && python monitor_pdv.py >> monitor_pdv.log 2>&1", 0, False
