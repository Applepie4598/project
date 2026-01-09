# project
Soc triage tool 
# SOC IP Triage Tool

Ett professionellt verktyg för Security Operations Center (SOC) som hjälper dig att analysera IP-adresser, identifiera hot och blockera farliga IPs i din brandvägg.

## 📋 Innehållsförteckning

- [Funktioner](#funktioner)
- [Installation](#installation)
- [Användning](#användning)
- [Teknisk Dokumentation](#teknisk-dokumentation)
- [Filstruktur](#filstruktur)
- [Exempel](#exempel)

---

## ✨ Funktioner

- ✅ **IP-validering** - Kontrollerar att IP-adressen är giltig (IPv4)
- ✅ **Privat IP-detektion** - Identifierar interna/privata IP-adresser
- ✅ **Threat Intelligence** - Jämför IPs mot databas med kända hot (C2-servrar, RATs, botnets, etc.)
- ✅ **Brandväggsintegration** - Blockera farliga IPs direkt i din brandvägg
- ✅ **Brandväggskontroll** - Kolla om en IP redan är blockerad
- ✅ **Loggning** - Alla aktiviteter loggas för revision
- ✅ **JSON-rapporter** - Genererar detaljerade rapporter för varje IP
- ✅ **Multi-OS Support** - Fungerar på Windows, Linux och macOS

---

## 🚀 Installation

### Krav
- Python 3.6 eller senare
- Administratörsrättigheter (för brandväggsblockering)

### Steg 1: Klona eller ladda ner projektet
```bash
cd brunosegnaprojekt
```

### Steg 2: Kontrollera att alla filer finns
```
brunosegnaprojekt/
├── main.py           # Huvudprogram
├── triage.py         # IP-analys och threat intelligence
├── firewall.py       # Brandväggshantering
├── Utils.py          # Hjälpfunktioner
├── data/             # Databas med kända hot-IPs
│   ├── Cobalt Strike C2 IPs.txt
│   ├── Metasploit Framework C2 IPs.txt
│   ├── AsyncRAT IPs.txt
│   └── ... (många fler)
└── logs/             # Skapas automatiskt
```

### Steg 3: Kör programmet
```bash
python main.py
```

---

## 📖 Användning

### Kommandoradsargument

#### 1. Kolla en specifik IP-adress
```bash
python main.py -ipv4 8.8.8.8
```

**Vad händer:**
- Validerar IP-adressen
- Kollar om det är en privat IP
- Kollar om IP:n är blockerad i brandväggen
- Jämför mot threat intelligence databas
- Genererar JSON-rapport
- Frågar om blockering (om IP:n är farlig och inte redan blockerad)

#### 2. Visa loggfilen
```bash
python main.py -checklog
```

**Visar:**
- Alla program-aktiviteter
- IP-kontroller
- Blockeringar
- Fel och varningar

#### 3. Visa rapport för specifik IP
```bash
python main.py -checklogip 192.168.1.1
```

**Visar:**
- JSON-rapport för den specifika IP:n
- Verdict, danger level, tidsstämpel, användare

#### 4. Interaktivt läge (ingen parameter)
```bash
python main.py
```

**Funktioner:**
- Kontinuerligt läge - programmet fortsätter köra
- Skriv in IP-adresser en efter en
- Skriv `exit`, `quit` eller `q` för att avsluta

---

## 🔧 Teknisk Dokumentation

### Arkitektur

Programmet består av 4 huvudmoduler:

#### **1. main.py** - Huvudprogram och användarinteraktion

**Ansvar:**
- Hantera kommandoradsargument med `argparse`
- Validera användarinput
- Koordinera mellan olika moduler
- Visa resultat till användaren

**Viktiga funktioner:**
- `is_private_ip(ip)` - Detekterar privata IP-adresser
  - `10.0.0.0/8` (10.0.0.0 - 10.255.255.255)
  - `172.16.0.0/12` (172.16.0.0 - 172.31.255.255)
  - `192.168.0.0/16` (192.168.0.0 - 192.168.255.255)
  - `127.0.0.0/8` (127.0.0.0 - 127.255.255.255) - Localhost

- `show_log()` - Läser och visar loggfilen
- `show_ip_report(ip)` - Läser och visar JSON-rapport för specifik IP
- `print_result(result)` - Formaterar och visar IP-analys resultat
- `main()` - Huvudfunktion som kör programmet

**Flöde:**
1. Parse kommandoradsargument
2. Setup logging, OS-check, permissions
3. Ladda blocked IPs från `data/` mappen
4. Hantera användarens kommando (-ipv4, -checklog, -checklogip, eller interaktivt)
5. Validera IP → Kolla privat → Analysera → Visa resultat → Fråga om blockering

---

#### **2. triage.py** - IP-analys och Threat Intelligence

**Ansvar:**
- Ladda threat intelligence data
- Analysera IP-adresser
- Generera rapporter
- Bestämma hotnivå

**Viktiga funktioner:**
- `load_blocked_ips(live_ip_folder="data")`
  - Läser alla `.txt` filer i `data/` mappen
  - Extraherar alla giltiga IPv4-adresser
  - Returnerar en `set` med alla kända farliga IPs

- `is_valid_ipv4(ip)`
  - Validerar IP-format med regex
  - Pattern: `^(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}$`
  - Varje oktet måste vara 0-255

- `triage_ip(ip, blocked_ips)`
  - Kollar om IP är blockerad i brandväggen
  - Jämför mot threat intelligence databas
  - Bestämmer `verdict` (BLOCKED/NOT BLOCKED IN FIREWALL)
  - Bestämmer `danger_level` (DANGEROUS/NOT_DANGEROUS/UNKNOWN)
  - Skapar resultat-dictionary med metadata

- `save_report(result)`
  - Sparar JSON-rapport som `report_<IP>.json`
  - Innehåller: IP, verdict, danger_level, timestamp, användare

- `scan_folder_for_bad_ips(folder_to_scan="data", live_ip_folder="data")`
  - Skannar en mapp efter IPs
  - Jämför mot threat intelligence
  - Rapporterar farliga IPs

**Threat Intelligence Databas:**
Programmet använder data från `data/` mappen med kända hot-IPs från:
- C2-servrar (Cobalt Strike, Metasploit, Sliver, Mythic, etc.)
- RATs (AsyncRAT, Quasar RAT, NanoCore, njRAT, etc.)
- Botnets (Mozi, 7777 Botnet)
- Phishing (GoPhish)
- Malware (DarkComet, SpyAgent, ShadowPad)

---

#### **3. firewall.py** - Brandväggshantering

**Ansvar:**
- Detektera operativsystem
- Blockera IPs i brandväggen
- Kontrollera om IPs är blockerade

**Viktiga funktioner:**
- `get_os_type()` - Returnerar OS-typ (Windows/Linux/Darwin)

- `is_ip_blocked_windows(ip)`
  - Kommando: `netsh advfirewall firewall show rule name=SOC_Block_<IP>`
  - Kollar om regeln finns i Windows Firewall

- `is_ip_blocked_linux(ip)`
  - Kommando: `sudo iptables -L INPUT -v -n`
  - Kollar om IP finns i iptables regler

- `is_ip_blocked_mac(ip)`
  - Kommando: `sudo pfctl -t blocklist -T show`
  - Kollar om IP finns i pfctl blocklist

- `is_ip_blocked_in_firewall(ip)`
  - Wrapper-funktion som väljer rätt OS-specifik funktion

- `block_ip_windows(ip)`
  - Kommando: `netsh advfirewall firewall add rule name=SOC_Block_<IP> dir=in action=block remoteip=<IP>`
  - Skapar inbound-regel som blockerar IP
  - Kräver Administrator-rättigheter

- `block_ip_linux(ip)`
  - Kommando: `sudo iptables -A INPUT -s <IP> -j DROP`
  - Lägger till DROP-regel i iptables
  - Kräver sudo-rättigheter

- `block_ip_mac(ip)`
  - Kommando: `sudo pfctl -t blocklist -T add <IP>`
  - Lägger till IP i pfctl blocklist
  - Kräver sudo-rättigheter

- `block_ip_in_firewall(ip)`
  - Wrapper-funktion som väljer rätt OS-specifik blockeringsfunktion
  - Visar OS-information och krav

- `ask_to_block_ip(ip)`
  - Frågar användaren om blockering
  - Anropar `block_ip_in_firewall()` vid "yes"

---

#### **4. Utils.py** - Hjälpfunktioner

**Ansvar:**
- Logging setup
- OS-validering
- Filrättigheter
- IP-validering

**Viktiga funktioner:**
- `setup_logging()`
  - Skapar `logs/` mapp om den inte finns
  - Konfigurerar logging till `logs/soc_ip_triage.log`
  - Format: `%(asctime)s | %(levelname)s | %(message)s`
  - Level: INFO

- `check_os()`
  - Kollar operativsystem med `platform.system()`
  - Stödda: Windows, Linux, Darwin (macOS)
  - Avslutar programmet om OS inte stöds

- `check_log_permissions()`
  - Testar att skriva till loggfilen
  - Avslutar programmet om inga skrivrättigheter

- `is_valid_ipv4(ip)`
  - Samma som i `triage.py`
  - Validerar IPv4-format

---

### Dataflöde

```
Användare kör: python main.py -ipv4 156.238.243.16
         ↓
    main.py startar
         ↓
    Setup (logging, OS-check, permissions)
         ↓
    Ladda blocked_ips från data/ mappen
         ↓
    Validera IP-format (Utils.is_valid_ipv4)
         ↓
    Kolla om privat IP (main.is_private_ip)
         ↓
    Analysera IP (triage.triage_ip)
         ├→ Kolla brandvägg (firewall.is_ip_blocked_in_firewall)
         ├→ Jämför mot blocked_ips (threat intelligence)
         └→ Skapa resultat-dictionary
         ↓
    Spara rapport (triage.save_report)
         ↓
    Visa resultat (main.print_result)
         ↓
    Om DANGEROUS + NOT BLOCKED → Fråga om blockering
         ↓
    firewall.ask_to_block_ip()
         ├→ Användare svarar "yes"
         └→ firewall.block_ip_in_firewall()
              ├→ Windows: netsh advfirewall
              ├→ Linux: iptables
              └→ macOS: pfctl
```

---

## 📁 Filstruktur

```
brunosegnaprojekt/
│
├── main.py                    # Huvudprogram (191 rader)
├── triage.py                  # IP-analys (117 rader)
├── firewall.py                # Brandväggshantering (138 rader)
├── Utils.py                   # Hjälpfunktioner (52 rader)
├── README.md                  # Denna fil
│
├── data/                      # Threat Intelligence databas
│   ├── all.txt                # Alla IPs samlade
│   ├── Cobalt Strike C2 IPs.txt
│   ├── Metasploit Framework C2 IPs.txt
│   ├── AsyncRAT IPs.txt
│   └── ... (40+ filer med kända hot-IPs)
│
├── logs/                      # Skapas automatiskt
│   └── soc_ip_triage.log      # Alla program-aktiviteter
│
└── report_*.json              # Genereras för varje IP-kontroll
```

---

## 💡 Exempel

### Exempel 1: Kolla en farlig IP (första gången)

```bash
$ python main.py -ipv4 156.238.243.16

==================================================
IP Address: 156.238.243.16
Verdict: NOT BLOCKED IN FIREWALL
Danger Level: DANGEROUS
Checked At: 2026-01-09T14:30:00.000000Z
User: bruno
==================================================

==================================================
Do you want to block this IP in your firewall? (yes/no): yes

==================================================
FIREWALL BLOCKING
==================================================
Operating System: Windows
IP to block: 156.238.243.16

Note: You may need to run this program as Administrator

[*] Blocking IP on Windows Firewall...
[+] Successfully blocked IP: 156.238.243.16
```

### Exempel 2: Kolla samma IP igen (efter blockering)

```bash
$ python main.py -ipv4 156.238.243.16

==================================================
IP Address: 156.238.243.16
Verdict: BLOCKED IN FIREWALL
Danger Level: DANGEROUS
Checked At: 2026-01-09T14:35:00.000000Z
User: bruno
==================================================
```
*Ingen fråga om blockering eftersom IP:n redan är blockerad!*

### Exempel 3: Kolla en säker IP (Google DNS)

```bash
$ python main.py -ipv4 8.8.8.8

==================================================
IP Address: 8.8.8.8
Verdict: NOT BLOCKED IN FIREWALL
Danger Level: NOT_DANGEROUS
Checked At: 2026-01-09T14:40:00.000000Z
User: bruno
==================================================
```
*Ingen fråga om blockering eftersom IP:n inte är farlig*

### Exempel 4: Försök kolla en privat IP

```bash
$ python main.py -ipv4 192.168.1.1

[!] This is an internal/private IP address
Internal IPs are not public and cannot be reached from the internet
```

### Exempel 5: Ogiltig IP-adress

```bash
$ python main.py -ipv4 999.999.999.999

[!] Invalid IPv4 address: 999.999.999.999
Valid example: 192.168.1.1
Each number must be between 0-255
```

### Exempel 6: Visa loggfilen

```bash
$ python main.py -checklog

==================================================
LOG FILE CONTENTS
==================================================
2026-01-09 14:30:00,123 | INFO | Program started
2026-01-09 14:30:00,125 | INFO | OS check passed: Windows
2026-01-09 14:30:00,127 | INFO | Log file permission OK
2026-01-09 14:30:01,200 | INFO | Checking IP: 156.238.243.16
2026-01-09 14:30:01,205 | INFO | Result: {'ip': '156.238.243.16', 'verdict': 'NOT BLOCKED IN FIREWALL', 'danger_level': 'DANGEROUS', ...}
2026-01-09 14:30:15,300 | INFO | Blocked IP in Windows Firewall: 156.238.243.16
==================================================
```

### Exempel 7: Visa rapport för specifik IP

```bash
$ python main.py -checklogip 156.238.243.16

==================================================
REPORT FOR IP: 156.238.243.16
==================================================
{
    "ip": "156.238.243.16",
    "verdict": "BLOCKED IN FIREWALL",
    "danger_level": "DANGEROUS",
    "checked_at": "2026-01-09T14:35:00.000000Z",
    "user": "bruno"
}
==================================================
```

### Exempel 8: Interaktivt läge

```bash
$ python main.py

==================================================
SOC IP Triage Tool - Interactive Mode
==================================================
Type 'exit' or 'quit' to stop the program

Enter IP address to check: 8.8.8.8

==================================================
IP Address: 8.8.8.8
Verdict: NOT BLOCKED IN FIREWALL
Danger Level: NOT_DANGEROUS
Checked At: 2026-01-09T14:45:00.000000Z
User: bruno
==================================================

Enter IP address to check: 156.238.243.16

==================================================
IP Address: 156.238.243.16
Verdict: BLOCKED IN FIREWALL
Danger Level: DANGEROUS
Checked At: 2026-01-09T14:45:30.000000Z
User: bruno
==================================================

Enter IP address to check: exit

Exiting program. Goodbye!
```

---

## 🔒 Säkerhet och Rättigheter

### Windows
- **Krav:** Kör PowerShell/CMD som **Administrator**
- **Högerklicka** på PowerShell → "Run as Administrator"
- Annars får du felmeddelande vid blockering

### Linux
- **Krav:** Sudo-rättigheter
- Programmet anropar `sudo iptables`
- Du kan behöva ange ditt lösenord

### macOS
- **Krav:** Sudo-rättigheter
- Programmet anropar `sudo pfctl`
- Du kan behöva ange ditt lösenord

---

## 🛠️ Felsökning

### Problem: "Cannot write to log file"
**Lösning:** Kontrollera att du har skrivrättigheter i mappen. Kör som Administrator/sudo.

### Problem: "Unsupported operating system"
**Lösning:** Programmet stöder endast Windows, Linux och macOS.

### Problem: Blockering fungerar inte på Windows
**Lösning:** Kör programmet som Administrator.

### Problem: Blockering fungerar inte på Linux/macOS
**Lösning:** Kontrollera att du har sudo-rättigheter och att iptables/pfctl är installerat.

### Problem: "Live IP folder 'data' not found"
**Lösning:** Kontrollera att `data/` mappen finns och innehåller `.txt` filer med IPs.

---

## 📊 Tekniska Detaljer

### IP-validering Regex
```regex
^(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}$
```

**Förklaring:**
- `25[0-5]` - Matchar 250-255
- `2[0-4]\d` - Matchar 200-249
- `1?\d?\d` - Matchar 0-199
- Upprepas 4 gånger separerat med `.`

### Privata IP-ranges (RFC 1918)
- **Class A:** 10.0.0.0/8 (16,777,216 adresser)
- **Class B:** 172.16.0.0/12 (1,048,576 adresser)
- **Class C:** 192.168.0.0/16 (65,536 adresser)
- **Loopback:** 127.0.0.0/8 (16,777,216 adresser)

### Brandväggskommandon

**Windows:**
```cmd
# Blockera IP
netsh advfirewall firewall add rule name=SOC_Block_156.238.243.16 dir=in action=block remoteip=156.238.243.16

# Kolla regel
netsh advfirewall firewall show rule name=SOC_Block_156.238.243.16
```

**Linux:**
```bash
# Blockera IP
sudo iptables -A INPUT -s 156.238.243.16 -j DROP

# Lista regler
sudo iptables -L INPUT -v -n
```

**macOS:**
```bash
# Blockera IP
sudo pfctl -t blocklist -T add 156.238.243.16

# Visa blocklist
sudo pfctl -t blocklist -T show
```

---

## 📝 Loggformat

```
YYYY-MM-DD HH:MM:SS,mmm | LEVEL | Message
```

**Exempel:**
```
2026-01-09 14:30:00,123 | INFO | Program started
2026-01-09 14:30:00,125 | INFO | OS check passed: Windows
2026-01-09 14:30:01,200 | WARNING | Invalid IP entered: 999.999.999.999
2026-01-09 14:30:15,300 | ERROR | Failed to block IP in Windows Firewall: 1.2.3.4
```

---

## 🎯 Use Cases

### 1. SOC Analyst - Snabb IP-kontroll
En SOC-analytiker ser en misstänkt IP i loggar och vill snabbt kolla om den är känd som farlig.
```bash
python main.py -ipv4 47.94.23.151
```

### 2. Incident Response - Blockera hot
Under en incident behöver du snabbt blockera en C2-server.
```bash
python main.py -ipv4 156.238.243.16
# Svara "yes" för att blockera
```

### 3. Threat Hunting - Batch-analys
Du har en lista med IPs och vill kolla alla mot din threat intelligence.
```bash
# Lägg IPs i en fil och använd interaktivt läge
python main.py
# Klistra in IPs en efter en
```

### 4. Audit - Granska tidigare kontroller
Du vill se vilka IPs som har kontrollerats tidigare.
```bash
python main.py -checklog
```

---

## 🔄 Framtida Förbättringar

- [ ] API-integration (VirusTotal, AbuseIPDB, etc.)
- [ ] Automatisk uppdatering av threat intelligence databas
- [ ] GUI-interface
- [ ] Batch-import från fil
- [ ] Export till CSV/Excel
- [ ] Statistik och dashboards
- [ ] Avblockera IPs
- [ ] Whitelist-hantering från fil
- [ ] Email-notifieringar
- [ ] SIEM-integration

---

## 👨‍💻 Utvecklare

**äppelkaka**

---

## 📄 Licens

Detta projekt är skapat för utbildnings- och säkerhetsändamål.

---

## ⚠️ Disclaimer

Detta verktyg är avsett för legitim säkerhetsanalys och incident response. Använd det ansvarsfullt och endast på system du har tillåtelse att analysera och modifiera.

---

**Skapad:** 2026-01-09
**Version:** 1.0
**Python Version:** 3.6+

