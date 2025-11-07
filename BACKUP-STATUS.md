# Backup-Status - Raspberry Pi → Arbeitsverzeichnis

**Letzte Synchronisation: 4. November 2025, 08:45 Uhr**

## ✅ Vollständig gesicherte Dateien

### Boot-Konfiguration
| Datei auf Pi | Gesichert in | Status |
|--------------|--------------|--------|
| `/boot/firmware/cmdline.txt` | `config-backup/cmdline.txt.FINAL` | ✅ Identisch |
| `/boot/firmware/config.txt` | `config-backup/config.txt.FINAL` | ✅ Identisch |

### Systemd Service
| Datei auf Pi | Gesichert in | Status |
|--------------|--------------|--------|
| `/etc/systemd/system/thinkcity-dashboard.service` | `config-backup/thinkcity-dashboard.service.FINAL` | ✅ Identisch |

# Backup-Status - Raspberry Pi → Arbeitsverzeichnis

**Letzte Synchronisation: 5. November 2025, ~12:00 Uhr**

## ✅ Vollständig gesicherte Dateien

### Python-Dateien (Core)
| Datei auf Pi | Gesichert in | Status |
|--------------|--------------|--------|
| `/home/pi/thinkcity-dashboard-v3/dashboard.py` | `dashboard.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/can_decoder.py` | `can_decoder.py` | ✅ Identisch (37 IDs, 100% coverage) |
| `/home/pi/thinkcity-dashboard-v3/can_interface.py` | `can_interface.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/trip_computer.py` | `trip_computer.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/db_manager.py` | `db_manager.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/trace_parser.py` | `trace_parser.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/trace_player.py` | `trace_player.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/translations.py` | `translations.py` | ✅ Identisch |

### Python-Dateien (UI)
| Datei auf Pi | Gesichert in | Status |
|--------------|--------------|--------|
| `/home/pi/thinkcity-dashboard-v3/widgets.py` | `widgets.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/main_screen.py` | `main_screen.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/battery_screen.py` | `battery_screen.py` | ✅ Identisch (mit module voltages) |
| `/home/pi/thinkcity-dashboard-v3/cells_screen.py` | `cells_screen.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/charge_screen.py` | `charge_screen.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/rawdata_screen.py` | `rawdata_screen.py` | ✅ Identisch |
| `/home/pi/thinkcity-dashboard-v3/settings_screen.py` | `settings_screen.py` | ✅ Identisch (mit trace controls) |

### CAN-Traces
| Datei auf Pi | Gesichert in | Status | Größe |
|--------------|--------------|--------|-------|
| `/home/pi/traces/*.trc` | `traces/*.trc` | ✅ Identisch | ~33 MB |
| `(PCAN Original)` | `../AKKU/191210_PCAN-Traces/*.trc` | ✅ Archiviert | ~100+ MB |

### Dokumentation
| Datei | Status | Beschreibung |
|-------|--------|--------------|
| `README.md` | ✅ Aktualisiert (5. Nov) | Module voltages, trace replay, 100% coverage |
| `README_DE.md` | ✅ Aktualisiert (5. Nov) | Deutsche Version synchronisiert |
| `PROJECT.md` | ✅ Aktualisiert (5. Nov) | Vollständige Projektstruktur mit neuen Features |
| `CAN_REFERENCE.md` | ✅ Aktualisiert (5. Nov) | 37 IDs dokumentiert, inkl. 0x4B0 |
| `DEVELOPMENT.md` | ✅ Aktualisiert (5. Nov) | Trace replay details |
| `TRACE_REPLAY_CONCEPT.md` | ✅ Aktualisiert (5. Nov) | Vollständige Implementierungs-Dokumentation |
| `SUMMARY.md` | ✅ Aktualisiert (5. Nov) | Entwicklungs-Übersicht komplett |
| `INSTALL.md` | ⚠️ Zu prüfen | Gemischte DE/EN Einträge, muss aufgeräumt werden |
| `INSTALL_DE.md` | ⚠️ Zu prüfen | Veraltete Version |
| `NEUINSTALLATION.md` | ⚠️ Zu prüfen | Installations-Guide veraltet? |
| `config-backup/WORKING-CONFIG.md` | ⚠️ Zu prüfen | Veraltet |
| `config-backup/FINAL-WORKING-SETUP.md` | ⚠️ Zu prüfen | Veraltet |

## Wichtige Erkenntnisse

### Aktuelle Features auf Pi (5. Nov 2025):
1. ✅ **37 CAN-IDs, 100% Decoder Coverage**
2. ✅ **Module Voltages (0x4B0)** im Battery Screen
3. ✅ **Trace Replay System** mit Start/Pause/Stop UI
4. ✅ **Bilingual UI** (DE/EN Sprachumschaltung)
5. ✅ **6 Screens** (Main, Battery, Cells, Charge, RawData, Settings)
6. ✅ **Settings mit Trace Controls** und Auto-Start on Boot
7. ✅ **Field Testing erfolgreich** - User: "ich habe den Trace bereits gestartet und es sieht ganz gut aus"

### Deployment-Methode:
- **rsync** vom lokalen Repo zum Pi
- **Kein Git auf Pi** (nur Deployment-Target)
- Systemd Service Auto-Start
- vcan0 für Trace Replay Tests

### Unterschiede Pi ↔ Lokal (alle behoben):
1. **can_interface.py**: 
   - ✅ Default `channel="vcan0"` auf Pi für Tests
   - Umgebungsvariable `TC_CAN_CHANNEL` überschreibt Default
   - Für Produktion: `TC_CAN_CHANNEL=can0` setzen

2. **Service-Datei**:
   - ✅ `Environment=TC_CAN_CHANNEL=vcan0` auf Pi
   - Für Produktion auf `can0` ändern

## Dateien NUR auf Pi (nicht relevant für Backup)

- `/home/pi/thinkcity-dashboard-v3/*.pyc` - Python-Bytecode (automatisch generiert)
- `/home/pi/thinkcity-dashboard-v3/__pycache__/` - Cache-Verzeichnis
- `/home/pi/thinkcity-dashboard-v3/thinkcity.db` - Laufzeit-Datenbank (wird automatisch erstellt)
- `/tmp/can_replay.log` - Temporäre Log-Datei

## Verifikation

### Checksummen-Vergleich (wichtigste Dateien)
```bash
# Dashboard-Code
md5sum dashboard.py
md5sum trip_computer.py
md5sum can_interface.py

# Dann auf Pi:
ssh pi@10.42.0.214 "cd /home/pi/thinkcity-dashboard-v3 && md5sum dashboard.py trip_computer.py can_interface.py"
```

### Automatische Synchronisation (optional)
Für zukünftige Updates könnte ein Sync-Script erstellt werden:
```bash
#!/bin/bash
# sync-from-pi.sh
sshpass -p 'raspberri' scp pi@10.42.0.214:/home/pi/thinkcity-dashboard-v3/{dashboard.py,trip_computer.py,can_interface.py} ./
sshpass -p 'raspberri' scp pi@10.42.0.214:/etc/systemd/system/thinkcity-dashboard.service ./config-backup/
sshpass -p 'raspberri' scp pi@10.42.0.214:/boot/firmware/{cmdline.txt,config.txt} ./config-backup/
```

## Nächste Schritte

- [ ] ✅ **Dokumentation** (in Arbeit - systematisch alle .md Dateien aktualisieren)
  - [x] README.md / README_DE.md
  - [x] PROJECT.md
  - [x] CAN_REFERENCE.md
  - [x] DEVELOPMENT.md
  - [x] TRACE_REPLAY_CONCEPT.md
  - [x] SUMMARY.md
  - [x] BACKUP-STATUS.md
  - [ ] INSTALL.md / INSTALL_DE.md (DE/EN Trennung)
  - [ ] NEUINSTALLATION.md
  - [ ] config-backup/*.md
- [ ] CAN-Hardware am Auto testen (MCP2515 mit echtem CAN-Bus)
- [ ] Reverse Engineering der unbekannten IDs (0x460, 0x495, 0x4CA)
- [ ] GPS-Integration
- [ ] WLAN-Sync zu NAS/InfluxDB
