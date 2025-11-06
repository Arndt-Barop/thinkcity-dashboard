# ThinkCity Dashboard v3 - Projektstruktur

## 📁 Datei-Übersicht

```
thinkcity-dashboard-v3/
│
├── README.md                      # Projekt-Dokumentation
├── INSTALL.md                     # Installations-Anleitung
├── requirements.txt               # Python Dependencies
├── setup.sh                       # Auto-Installer (Bash)
├── start_dashboard.sh            # Manueller Starter
│
├── dashboard.py                   # 🎯 Haupt-Anwendung
├── can_interface.py              # CAN-Bus Manager (retry-logic)
├── can_decoder.py                # CAN Frame Decoder (alle IDs)
├── db_manager.py                 # SQLite Manager (auto-trips)
├── trip_computer.py              # Range/Consumption Calculator
│
├── widgets.py                    # UI-Widgets (Gauge, Display, Battery)
├── main_screen.py                # Hauptbildschirm (Speed, Power, Range)
├── battery_screen.py             # Batterie-Details
├── charge_screen.py              # Lade-Ansicht
│
└── systemd/
    ├── thinkcity-dashboard.service    # Dashboard Service
    └── can-interface.service          # CAN Setup Service
```

---

## 🔧 Modul-Beschreibungen

### **dashboard.py** (300 Zeilen)
Haupt-Anwendung die alles zusammenführt.

**Features:**
- 3 Screens mit Touch-Navigation
- CAN-Bus Integration + Auto-Reconnect
- Auto-Logging (1 Hz)
- Trip-Computer Integration

**Environment Variables:**
- `QT_QPA_PLATFORM`: Display Backend (xcb|linuxfb|eglfs)
- `TC_FULLSCREEN`: 1=Fullscreen, 0=Fenster
- `TC_HIDE_CURSOR`: Cursor verstecken
- `TC_CAN_CHANNEL`: CAN Interface (default: can0)
- `TC_DB_PATH`: Datenbank-Pfad

---

### **can_interface.py** (180 Zeilen)
Robuste CAN-Bus-Schnittstelle.

**Features:**
- Auto-Retry bei Verbindungsfehlern (max 10x)
- Interface-Existenz-Check vor Connect
- Reconnect-Funktion
- Helper für manuelle Interface-Konfiguration
- CLI-Test-Modus

**Löst:** Race-Condition-Problem der ChatGPT-Version

---

### **can_decoder.py** (330 Zeilen)
Dekodiert alle ThinkCity CAN-Messages.

**Unterstützte IDs:**
- `0x301-0x305`: BMI (Battery Management)
- `0x263`: General (Speed, Ambient Temp, Mains)
- `0x264`: Shifter (P/R/N/D/E)
- `0x311`: Max AC Current
- `0x610-0x611`: EnerDel (Cell Voltages, SOC)

**Features:**
- Automatische Zebra/EnerDel-Erkennung
- SOH-Schätzung aus Zellspannungs-Delta
- Sichere Frame-Verarbeitung (fehlerhafte Bytes → Fallback)
- State-Merging mit intelligenter SOC-Auswahl

---

### **db_manager.py** (360 Zeilen)
SQLite-Datenbank-Manager.

**Features:**
- **Auto-Trip-Detection**: Start bei >1 km/h, Ende nach 5min Idle
- GPS-ready: `latitude`/`longitude` Spalten
- Sync-Status für WLAN-Upload
- Lifetime-Statistiken
- Context-Manager für sichere Transaktionen

**Tabellen:**
- `trips`: Fahrten-Übersicht
- `samples`: Messdaten (1 Hz)

---

### **trip_computer.py** (180 Zeilen)
Reichweiten- & Verbrauchs-Berechnung.

**Features:**
- **Welford-Algorithmus** für stabile Mittelwerte
- Verbrauch: Jetzt / Trip / Lifetime
- Reichweite: `(SOC/100) × 24kWh × 1000 / avg_wh_km`
- Trip-Reset & Statistiken
- Konfigurierbare Batterie-Kapazität

**Fehlte in ChatGPT-Version komplett!**

---

### **widgets.py** (320 Zeilen)
Wiederverwendbare UI-Komponenten.

**Widgets:**
- `PowerGauge`: Halbkreis-Anzeige (-30 bis +30 kW)
- `DigitalDisplay`: Große Touch-freundliche Anzeigen
- `BatteryBar`: Horizontaler SOC-Balken mit Farben
- `TouchButton`: Custom Button mit Callback

**Alle mit Live-Preview-Test!**

---

### **main_screen.py** (145 Zeilen)
Haupt-Bildschirm.

**Zeigt:**
- Geschwindigkeit (groß, 80pt)
- Power Gauge (Halbkreis)
- Reichweite & Verbrauch
- SOC-Balken + SOH

---

### **battery_screen.py** (280 Zeilen)
Batterie-Details.

**Zeigt:**
- Spannungen & Ströme
- Zellspannungen (Min/Max/Avg/Delta) - nur EnerDel
- Temperaturen (Pack, Ambient)
- Status-Flags (Laden, Entladen, ISO-Fehler, etc.)
- Batterie-Typ (EnerDel / Zebra)

---

### **charge_screen.py** (250 Zeilen)
Lade-Ansicht.

**Features:**
- Ladestatus-Erkennung (AC-Spannung + Charge-Flag)
- Zeit-Schätzungen (verstrichen, verbleibend, fertig um)
- AC Spannung/Strom
- DC Ladeleistung
- Geladene Energie (kWh)

**Berechnung:** Lineare Extrapolation aus bisheriger Lade-Rate

---

### **setup.sh** (384 Zeilen)
Automatischer Installer.

**9 Installations-Schritte:**
1. System Update
2. Python-Pakete (PyQt5, can-utils, X11)
3. Python-Dependencies (pip)
4. MCP2515 SPI-Konfiguration (device-tree)
5. USB-SSD Auto-Mount (UUID-basiert)
6. Boot-Optimierung (Bluetooth off, quiet boot)
7. Systemd-Services
8. Auto-Login (pi user)
9. Auto-Start X11 + Dashboard

**Features:** Farb-Output, Error-Handling, Bestätigung vor kritischen Schritten

---

### **systemd/thinkcity-dashboard.service**
Systemd Service für Dashboard.

**Features:**
- Wartet auf `can-interface.service`
- Prüft CAN-Interface-Existenz (`ConditionPathExists`)
- Auto-Restart bei Fehler
- Journal-Logging

---

### **systemd/can-interface.service**
Systemd Service für CAN-Setup.

**Features:**
- Konfiguriert can0 (500 kbit/s)
- `RemainAfterExit=yes` für Dependency-Tracking
- Läuft vor Dashboard-Start

---

## 🎯 Workflow

```
Boot → Systemd
  ↓
can-interface.service
  - ip link set can0 type can bitrate 500000
  - ip link set can0 up
  ↓
thinkcity-dashboard.service
  - Startet dashboard.py
  ↓
dashboard.py
  - Initialisiert CANInterface
  - Erstellt Screens (Main, Battery, Charge)
  - Startet Update-Loop (10 Hz)
  - Startet Logging-Loop (1 Hz)
  ↓
CAN-Loop:
  - can_interface.receive()
  - can_decoder.parse()
  - can_decoder.merge_state()
  - trip_computer.update()
  - screen.update_data()
  ↓
Logging-Loop:
  - db_manager.add_sample()
  - Auto-Trip-Detection
```

---

## 🔄 Vergleich zu ChatGPT v2

| Feature | ChatGPT v2 | Dashboard v3 |
|---------|------------|--------------|
| **Display Backend** | EGLFS only ❌ | 3 Optionen ✅ |
| **CAN Init** | Race Condition ❌ | Retry-Logic ✅ |
| **Trip-Computer** | Fehlt ❌ | Komplett ✅ |
| **Auto-Trip-Detection** | Fehlt ❌ | 5min Idle ✅ |
| **SOH-Berechnung** | Fehlt ❌ | Zell-Delta ✅ |
| **Zebra-Unterstützung** | Nein ❌ | Ja ✅ |
| **DB-Pfad** | Hardcoded ❌ | Env-Variable ✅ |
| **Fehler-Handling** | Crash ❌ | Fallbacks ✅ |
| **GPS-Support** | Nein ❌ | Schema ready ✅ |

---

## 📊 Performance-Schätzung (Pi 4B)

| Komponente | CPU | RAM | Boot-Zeit |
|------------|-----|-----|-----------|
| **Linux Kernel** | 4% | 80 MB | 2s |
| **Systemd Services** | 2% | 20 MB | 1.5s |
| **X11 (openbox)** | 4% | 50 MB | 3s |
| **PyQt5 GUI** | 12% | 120 MB | 1.5s |
| **CAN-Bus Handling** | 3% | 10 MB | - |
| **SQLite Logging** | 2% | 5 MB | - |
| **────────────** | **27%** | **285 MB** | **~8s** |

**Reserve:** 73% CPU, 1715+ MB RAM (bei 2 GB Modell) für zukünftige Features!

---

## 🚀 Next Steps / Future Features

### Phase 1 - Core (DONE ✅)
- ✅ CAN-Bus Integration
- ✅ Haupt-Screens (3x)
- ✅ Trip-Computer
- ✅ Auto-Logging

### Phase 2 - Connectivity (TODO)
- ⏳ WLAN-Sync zu InfluxDB/MQTT
- ⏳ GPS-Integration (USB-Dongle)
- ⏳ Mobile App (View-Only)

### Phase 3 - Advanced (TODO)
- ⏳ Settings-Screen (Kalibrierung)
- ⏳ History-Screen (vergangene Trips)
- ⏳ OTA-Updates
- ⏳ Diagnose-Codes (DTCs)

### Phase 4 - Optional (IDEAS)
- 💡 Video-Dashcam
- 💡 Navigation (OpenStreetMap)
- 💡 Audio-Player
- 💡 Rear-View-Camera

---

**Gesamtumfang:** ~2500 Zeilen Python + 400 Zeilen Bash + 1500 Zeilen Doku = **4400 Zeilen**

**Entwicklungszeit:** ~8 Stunden (mit KI-Unterstützung)

**Code-Qualität:** 
- ✅ Type Hints
- ✅ Docstrings
- ✅ Error Handling
- ✅ Test-Modi
- ✅ Logging
- ✅ Konfigurierbar

---

## 📞 Kontakt / Beitragen

```bash
# Bugs / Feature-Requests
https://github.com/yourusername/thinkcity-dashboard-v3/issues

# Pull Requests willkommen!
```

---

**Lizenz:** MIT (siehe LICENSE)

**Credits:** 
- Original BASIC Code: ThinkCity Community
- CAN Database: SavvyCAN Project
- ChatGPT v2: Baseline Reference
