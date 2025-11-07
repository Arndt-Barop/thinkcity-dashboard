# Development Features

## ⚙️ Settings-Screen

Das Dashboard enthält einen **Settings-Screen** (⚙️ Button in der Navigation) für grundlegende Konfiguration.

### Funktionen

**CAN-Interface:**
- Auswahl zwischen `can0` (Hardware) und `vcan0` (Virtual CAN for testing)
- Automatischer Start des CAN-Trace-Replays beim Boot (nur für vcan0)

**WLAN:**
- Heim-WLAN SSID konfigurieren
- Sync nur bei WLAN-Verbindung aktivieren

**NAS-Synchronisation:**
- NAS Host/IP (z.B. `192.168.1.100` oder `nas.local`)
- NAS Pfad (z.B. `/backup/thinkcity`)
- Benutzer für SSH/SMB-Zugang
- Automatisches Backup nach jeder Fahrt

**Datenbank:**
- Pfad zur SQLite-Datenbank anpassen

**📊 Logging-Konfiguration:**
- **Logging aktivieren/deaktivieren**: Komplettes Ein/Ausschalten des Dataloggings
- **Log-Intervall**: 1-60 Sekunden (Slider)
  - 1s = hohe Genauigkeit, viele Daten, großer Speicher
  - 60s = grobe Übersicht, wenig Daten, kleiner Speicher
- **Datenpunkt-Auswahl**: Wähle welche Werte geloggt werden sollen (25+ Felder):
  - **Grunddaten**: 🚗 Geschwindigkeit, 🔋 SOC, ⚡ Spannung, Strom, Leistung
  - **Temperaturen**: 🌡️ Akku max/min/Durchschnitt, Außentemperatur
  - **Zellspannungen**: max/min/avg/delta
  - **Modulspannungen**: 4 Module + Gesamt
  - **Fehlerflags**: ISO-Fehler, Notfall, System-Fehler
  - **Berechnet**: 📊 Verbrauch Wh/km, 📏 Reichweite, 🛣️ Kilometerstand
- **Permanent geloggt**: Durchschnittsverbrauch, **SOH (State of Health)**
- **Alle/Keine** Buttons zum schnellen Auswählen

**🔧 Bordcomputer:**
- **Trip Computer zurücksetzen**: Strecke/Energie/Verbrauch auf 0
- **SOH zurücksetzen**: State of Health auf 100% (z.B. nach Batteriewechsel)
  - SOH wird mit exponentieller Glättung (alpha=0.001) getrackt
  - Persistiert in Datenbank (überlebt harten Shutdown)
  - Separater Reset-Button (orange) für SOH

**🔧 System-Steuerung:**
- **🔄 Neustart**: System neu starten (mit Bestätigung)
- **⏻ Herunterfahren**: System sauber herunterfahren (mit Bestätigung)
- Beide Funktionen erfordern sudo-Rechte (siehe Installation)

### Verwendung

1. Dashboard starten
2. Auf **⚙️** Button klicken
3. Einstellungen vornehmen
4. **💾 Speichern** klicken
5. Optional: **🔄 Neustart** oder **⏻ Herunterfahren** für System-Steuerung

Einstellungen werden in `~/thinkcity-dashboard-v3/config.json` gespeichert.

### Installation der sudo-Rechte

Für Shutdown/Reboot-Funktionen:

```bash
cd ~/thinkcity-dashboard-v3
chmod +x setup_sudo_permissions.sh
./setup_sudo_permissions.sh
```

Dies erlaubt dem `pi`-User passwortloses shutdown/reboot.

---

## 🎬 CAN Trace Replay

For development and testing without a real vehicle. Replays recorded PCAN traces on vcan0.

### Quick Start

1. **Copy PCAN .trc files** to `~/thinkcity-dashboard-v3/traces/`
   ```bash
   cp ~/path/to/your/*.trc ~/thinkcity-dashboard-v3/traces/
   ```

2. **Configure in Settings:**
   - Open Settings (⚙️ button)
   - CAN Interface: Select `vcan0`
   - Trace Replay: Select your .trc file from dropdown
   - Enable "Loop Playback" for continuous replay
   - Enable "Start on Boot" for automatic startup
   - Save settings

3. **Reboot or start manually:**
   ```bash
   # Automatic (after reboot with "Start on Boot" enabled)
   systemctl status can-trace-replay
   
   # Manual start
   python3 trace_player.py ~/thinkcity-dashboard-v3/traces/your-trace.trc --loop
   ```

### Architecture

**Components:**
- `trace_parser.py` - PCAN .trc format parser (supports v1.1)
- `trace_player.py` - CAN bus replay with original timing
- `can-trace-replay.service` - Systemd service for auto-start
- Settings UI - Trace selection dropdown with Start/Pause/Stop controls

**Format Support:**
- PCAN-View .trc files (Version 1.1)
- Original timing preserved (timestamps in milliseconds)
- All CAN IDs supported (37 unique IDs, 100% decoder coverage)
- Module voltages (0x4B0) included for battery diagnostics

### Testing Traces

Standalone test without CAN bus:
```bash
# Parse and analyze trace
python3 trace_parser.py ~/path/to/trace.trc

# Test player (requires vcan0)
# 1. Setup vcan0
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# 2. Play trace
python3 trace_player.py ~/path/to/trace.trc --loop

# 3. Monitor CAN traffic
candump vcan0
```

### Creating Your Own Traces

**Option 1: PCAN-View Recording**
1. Record with PCAN-View software
2. Export as .trc file (v1.1 format)
3. Copy to `~/thinkcity-dashboard-v3/traces/`

**Option 2: Convert from candump**
```bash
# Record with candump
candump can0 -l

# Convert to PCAN format (if converter available)
python3 tools/candump2trc.py candump-*.log > trace.trc
```

### Service Management

The `can-trace-replay.service` is automatically managed by Settings:
- **Enable/Disable:** Via "Start on Boot" checkbox
- **Trace Selection:** Reads `trace_file` from `config.json`
- **Loop Mode:** Configured via Settings

Manual service control:
```bash
# Status
systemctl status can-trace-replay

# Logs
journalctl -u can-trace-replay -f

# Manual control
sudo systemctl start can-trace-replay
sudo systemctl stop can-trace-replay
sudo systemctl enable can-trace-replay
sudo systemctl disable can-trace-replay
```

---

## 💾 NAS-Synchronisation

Automatisches Backup der Fahrdaten zum NAS bei WLAN-Verbindung.

### Voraussetzungen

**Hardware:**
- NAS mit SSH-Zugang **oder** SMB/CIFS-Share
- WLAN-Modul im Raspberry Pi

**Software:**
- `rsync` (für SSH-Sync)
- `wireless-tools` (für WLAN-Erkennung)
- Optional: `sshpass` (falls kein SSH-Key verwendet wird)

### Einrichtung

#### 1. NAS vorbereiten

**Backup-Verzeichnis erstellen:**
```bash
# Auf dem NAS (via SSH):
mkdir -p /backup/thinkcity
chmod 755 /backup/thinkcity
```

#### 2. SSH-Key Setup (empfohlen)

Für passwortlosen Sync:

```bash
# Auf dem Pi:
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Public Key zum NAS kopieren:
ssh-copy-id benutzer@nas-host

# Testen:
ssh benutzer@nas-host "echo 'SSH funktioniert!'"
```

#### 3. Settings-Screen konfigurieren

1. Dashboard öffnen → ⚙️ Settings
2. **WLAN** Sektion:
   - Heim-WLAN SSID eingeben (z.B. "MeinWLAN")
   - "Sync nur bei WLAN-Verbindung" aktivieren
3. **NAS Synchronisation** Sektion:
   - "NAS-Sync aktivieren" ✓
   - NAS Host/IP: `192.168.1.100` oder `nas.local`
   - NAS Pfad: `/backup/thinkcity`
   - Benutzer: `pi` (oder NAS-Benutzername)
4. Speichern

### Verwendung

**Automatisch (empfohlen):**

Sync erfolgt automatisch wenn:
- NAS-Sync aktiviert ist
- Mit konfiguriertem WLAN verbunden
- NAS erreichbar ist
- Fahrt beendet wurde (Geschwindigkeit = 0 für >5 Minuten)

**Manuell testen:**
```bash
# Einmalig ausführen:
python3 ~/thinkcity-dashboard-v3/tools/nas_sync.py

# Log anzeigen:
cat ~/thinkcity-dashboard-v3/nas_sync.log
```

**Automatisch per Cron (optional):**
```bash
crontab -e
# Zeile hinzufügen für stündlichen Sync:
0 * * * * /home/pi/thinkcity-dashboard-v3/tools/nas_sync.py
```

### Funktionsweise

1. **WLAN-Check**: Prüft ob mit konfiguriertem WLAN verbunden
2. **NAS-Erreichbarkeit**: Testet Port 445 (SMB) oder Ping
3. **Sync**: Kopiert Datenbank via `rsync` über SSH
4. **Backup-Name**: `thinkcity_YYYYMMDD_HHMMSS.db`
5. **Cleanup**: Behält die letzten 10 Backups, löscht ältere

### Troubleshooting

**NAS nicht erreichbar:**
```bash
# Testen:
ping nas-host
telnet nas-host 445  # SMB-Port
ssh benutzer@nas-host
```

**SSH-Passwort-Abfrage:**
- SSH-Key Setup durchführen (siehe oben)
- Oder `sshpass` verwenden (unsicherer)

**WLAN nicht erkannt:**
```bash
# Aktuelles WLAN prüfen:
iwgetid -r

# Verfügbare WLANs:
sudo iwlist wlan0 scan | grep ESSID
```

**Logs prüfen:**
```bash
# NAS Sync Log:
tail -f ~/thinkcity-dashboard-v3/nas_sync.log

# System-Log:
journalctl -f | grep nas_sync
```

### Backup wiederherstellen

```bash
# Vom NAS zum Pi kopieren:
scp benutzer@nas-host:/backup/thinkcity/thinkcity_20251104_183000.db \
    ~/thinkcity-dashboard-v3/thinkcity.db

# Dashboard neu starten:
sudo systemctl restart thinkcity-dashboard
```

---

## 🔧 Tipps für Entwicklung

### Schneller Workflow

1. **Trace-Replay aktivieren** für Tests ohne Auto
2. **Settings-Screen** nutzen für schnelle Änderungen
3. **Logs überwachen**:
   ```bash
   # Dashboard:
   journalctl -u thinkcity-dashboard -f
   
   # CAN Interface Setup:
   journalctl -u can-setup -f
   
   # NAS Sync:
   tail -f ~/thinkcity-dashboard-v3/nas_sync.log
   ```

### Code-Änderungen testen

```bash
# Dashboard neu starten:
sudo systemctl restart thinkcity-dashboard

# Oder manuell im Terminal (für Debug-Output):
cd ~/thinkcity-dashboard-v3
TC_CAN_CHANNEL=vcan0 python3 dashboard.py
```

### Datenbank zurücksetzen

```bash
# Backup erstellen:
cp thinkcity.db thinkcity.db.backup

# Neu initialisieren:
rm thinkcity.db
# Dashboard startet und erstellt neue DB automatisch
sudo systemctl restart thinkcity-dashboard
```

---

## 📊 NAS-Backup Analyse

Die synchronisierten Datenbanken können auf dem PC analysiert werden:

```bash
# DB vom NAS holen:
scp benutzer@nas:/backup/thinkcity/thinkcity_20251104_183000.db ./

# Mit SQLite Browser öffnen:
sqlitebrowser thinkcity_20251104_183000.db

# Oder via CLI:
sqlite3 thinkcity_20251104_183000.db
```

**Interessante Queries:**

```sql
-- Alle Fahrten anzeigen:
SELECT trip_id, start_time, end_time, distance_km, avg_consumption 
FROM trips 
ORDER BY start_time DESC;

-- Trip-Details:
SELECT * FROM trip_samples 
WHERE trip_id = 1 
ORDER BY timestamp;

-- Zellspannungen einer Fahrt:
SELECT timestamp, cell_voltages 
FROM samples 
WHERE timestamp BETWEEN '2025-11-04 10:00' AND '2025-11-04 11:00';
```

---

## 🗄️ Datenbank-Details

### Schema

**`trips` Tabelle** (Fahrt-Übersicht):
- Start/Ende: `start_time`, `end_time`
- Strecke: `start_odo_km`, `end_odo_km`, `distance_km`
- Energie: `start_soc_pct`, `end_soc_pct`, `energy_used_kwh`
- Verbrauch: `avg_consumption_wh_km`, `avg_consumption_kwh_100km`
- Leistung: `max_power_kw`, `min_power_kw`
- Geschwindigkeit: `avg_speed_kmh`, `max_speed_kmh`
- Sync: `synced` (0=noch nicht gesichert, 1=auf NAS)

**`samples` Tabelle** (Detail-Messwerte):
- Trip-Zuordnung: `trip_id`
- Zeitstempel: `timestamp`
- Alle konfigurierten Datenpunkte (siehe Settings)

### Logging-Konfiguration

**Standard-Einstellungen:**
- Intervall: 1 Sekunde (anpassbar 1-60s)
- Alle Datenpunkte aktiviert
- Automatischer Trip-Start bei Bewegung (`speed > 1 km/h`)
- Automatisches Trip-Ende nach 5 Minuten Stillstand

**Anpassung via Settings-Screen:**
1. Settings öffnen (⚙️)
2. Sektion "📊 Daten-Logging"
3. Intervall einstellen (1-60s Slider)
4. Datenpunkte auswählen/abwählen
5. Speichern → Änderungen sofort aktiv!

**Beispiel-Konfigurationen:**

*Minimal (nur Essentials, 10s Intervall):*
- Geschwindigkeit, SOC, Verbrauch, Odo
- ~600 Samples/Stunde → ~5 KB/Stunde

*Standard (alle außer GPS, 1s Intervall):*
- Alle außer GPS-Koordinaten
- ~6000 Samples/Stunde → ~50 KB/Stunde

*Komplett (alles, 1s Intervall):*
- Alle Datenpunkte inkl. GPS
- ~6000 Samples/Stunde → ~60 KB/Stunde

### Retention Policy

**Automatische Bereinigung:**
- Löscht Trips **älter als 90 Tage**
- Nur wenn `synced = 1` (bereits auf NAS gesichert)
- Läuft automatisch beim Beenden jedes Trips
- Löscht Trip + zugehörige Samples

**Manuelles VACUUM:**
- Wird beim Dashboard-Shutdown ausgeführt
- Defragmentiert Datenbank
- Gibt Speicher frei

**Speicherbedarf schätzen:**
```python
# Pro Sample: ~100 Bytes (abhängig von ausgewählten Feldern)
# 1 Stunde Fahrt @ 1s Intervall = 3600 Samples = ~350 KB
# 1 Jahr Daten (300 Fahrten, Ø 1h) = ~100 MB
# Mit 90-Tage Retention: ~25 MB
```

**Datenbank-Größe prüfen:**
```bash
# Auf dem Pi:
ls -lh ~/thinkcity-dashboard-v3/thinkcity.db

# Anzahl Trips:
sqlite3 thinkcity.db "SELECT COUNT(*) FROM trips;"

# Anzahl Samples:
sqlite3 thinkcity.db "SELECT COUNT(*) FROM samples;"

# Ältester/Neuester Trip:
sqlite3 thinkcity.db "SELECT MIN(start_time), MAX(start_time) FROM trips;"
```

---
