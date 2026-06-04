# Dataset Documentation

## Case 001 — Malware Infection via Phishing Email

### Overview
| Field | Value |
|-------|-------|
| Case ID | CASE-001 |
| Type | Malware infection |
| Vector | Phishing email |
| Platform | Windows workstation |
| Hostname | WORKSTATION-047 |
| User | john.smith |

### Evidence Files

| File | Size | Type | Description |
|------|------|------|-------------|
| suspicious_script.ps1 | 336 bytes | PowerShell | Malware dropper script |
| autorun.bat | 264 bytes | Batch | Persistence mechanism |
| system_info.txt | 305 bytes | Text | System state at infection time |
| readme.txt | 129 bytes | Text | Case documentation |

### Ground Truth

**What actually happened:**
1. Phishing email delivered malicious PowerShell script
2. Script downloaded payload from http://malicious-c2-server.com/payload.exe
3. Payload saved as C:\Windows\Temp\svchost32.exe
4. Registry key added for persistence at HKCU\...\Run
5. C2 communication established to 185.220.101.45:4444

### What the Agent Found
- ✅ PowerShell execution detected
- ✅ Suspicious files identified
- ✅ Download activity confirmed
- ✅ Persistence mechanism found
- ✅ Malware indicators present
- ✅ Timeline reconstructed
- ✅ File hashes calculated

### IOCs Extracted
| IOC | Type | Value |
|-----|------|-------|
| C2 Server | IP | 185.220.101.45 |
| C2 Port | Port | 4444 |
| Payload URL | URL | http://malicious-c2-server.com/payload.exe |
| Malicious binary | Filename | svchost32.exe |
| Registry key | Persistence | HKCU\Software\Microsoft\Windows\CurrentVersion\Run |

### Reproducibility
To reproduce this analysis:
1. Clone the repository
2. Follow setup instructions in README
3. Run `python main.py`
4. Results saved to `reports/` and `logs/`
