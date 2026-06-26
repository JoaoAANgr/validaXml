Dim shell, pasta
Set shell = CreateObject("WScript.Shell")
pasta = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
shell.Run "cmd /c cd /d """ & pasta & """ && python monitor_pdv.py >> monitor_pdv.log 2>&1", 0, False
