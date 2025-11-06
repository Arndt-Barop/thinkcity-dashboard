# ThinkCity Dashboard v3# ThinkCity Dashboard v3



**Modern PyQt5 Dashboard for Think City Electric Vehicles**  **Modernes PyQt5 Dashboard für Think City Elektrofahrzeuge**  

**Raspberry Pi 4B + HDMI Touchscreen + MCP2515 CAN****Raspberry Pi 4B + HDMI-Touchscreen + MCP2515 CAN**



A complete CAN bus dashboard for Raspberry Pi with SunFounder 10" HDMI touchscreen and MCP2515 CAN interface. Developed with Claude Sonnet 3.5 for precise CAN bus decoding and professional UI design.Ein vollwertiges CAN-Bus Dashboard für den Raspberry Pi mit SunFounder 10" HDMI-Touchscreen und MCP2515 CAN-Interface. Entwickelt mit Claude Sonnet 3.5 für präzise CAN-Bus-Dekodierung und professionelle UI-Gestaltung.



[🇩🇪 Deutsche Version](README_DE.md)## ⚠️ Disclaimer



## ⚠️ Disclaimer**Dieses Projekt ist nicht mit Think Global AS, Electric Mobility Solutions AS oder anderen Herstellern des Think City Fahrzeugs verbunden oder von diesen autorisiert.** "Think City" bezieht sich ausschließlich auf das Elektrofahrzeugmodell. Dieses Dashboard wurde als Community-Projekt für Besitzer von Think City Fahrzeugen entwickelt.



**This project is not affiliated with or authorized by Think Global AS, Electric Mobility Solutions AS, or any manufacturer of the Think City vehicle.** "Think City" refers solely to the electric vehicle model. This dashboard was developed as a community project for Think City vehicle owners.**This project is not affiliated with or authorized by Think Global AS, Electric Mobility Solutions AS, or any manufacturer of the Think City vehicle.** "Think City" refers solely to the electric vehicle model. This dashboard was developed as a community project for Think City vehicle owners.



------



## 📸 Screenshots## 📸 Screenshots



### Main Screen### Hauptscreen

![Main Screen](docs/images/screen1-main.png)![Main Screen](docs/images/screen1-main.png)

*Speed, Power Gauge (-50 to +200 kW), Range, Consumption, Drive Mode**Geschwindigkeit, Power-Gauge (-50 bis +200 kW), Range, Verbrauch, Fahrmodus*



### Battery Overview### Batterie-Übersicht

![Battery Screen](docs/images/screen2-battery.png)![Battery Screen](docs/images/screen2-battery.png)

*Voltages, Currents, Temperatures, SOC, SOH, Status Flags**Spannungen, Ströme, Temperaturen, SOC, SOH, Status-Flags*



### Cell Voltages### Zellspannungen

![Cell Voltages Screen](docs/images/screen3-cells.png)![Cell Voltages Screen](docs/images/screen3-cells.png)

*All 88 cells individually with bar graphs and color coding**Alle 88 Zellen einzeln mit Bargraphen und Farbcodierung*



### Charging Status### Ladestatus

![Charge Screen](docs/images/screen4-charge.png)![Charge Screen](docs/images/screen4-charge.png)

*AC/DC values, charging current, estimated charging time**AC/DC-Werte, Ladestrom, geschätzte Ladezeit*



### CAN Raw Data### CAN-Rohdaten

![Raw Data Screen](docs/images/screen5-rawdata.png)![Raw Data Screen](docs/images/screen5-rawdata.png)

*Live CAN traffic with ID reference table**Live CAN-Traffic mit ID-Referenztabelle*



------



![Dashboard Status](https://img.shields.io/badge/status-production%20ready-brightgreen)![Dashboard Status](https://img.shields.io/badge/status-production%20ready-brightgreen)

![Python](https://img.shields.io/badge/python-3.9+-blue)![Python](https://img.shields.io/badge/python-3.9+-blue)

![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204B-red)![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204B-red)



------



## ✨ Features## ✨ Features



### 📊 **6 Main Screens**### 📊 **5 Hauptscreens**



- **Main**: Speed, Power Gauge, Range, Consumption, Drive Mode (P/N/R/D/E)- **Haupt**: Geschwindigkeit, Power-Gauge, Range, Verbrauch, Fahrmodus (P/N/R/D/E)

- **Battery**: Voltages, Currents, Temperatures, Status Flags- **Batterie**: Spannungen, Ströme, Temperaturen, Status-Flags

- **Cells**: Detailed view of all 88 cell voltages with bar graphs- **Zellen**: Detaillierte Ansicht aller 88 Zellspannungen mit Bargraphen

- **Charge**: Charging status, AC/DC values, time estimates- **Laden**: Ladestatus, AC/DC-Werte, Zeitschätzungen

- **Raw Data**: Live CAN terminal + ID reference table- **Rohdaten**: Live CAN-Terminal + ID-Referenztabelle

- **Settings**: System configuration, CAN interface, Network, Logging, **Trace Replay**

### 🎛️ **Power-Gauge mit logarithmischer Skalierung**

### 🌍 **Bilingual UI (DE/EN)**

- Bereich: -50 kW (Rekuperation) bis +200 kW (Vollgas)

- Complete translation system with 150+ UI strings- Pseudo-logarithmische Skalierung für bessere Auflösung im Normalbereich (0-30 kW)

- Language switcher in Settings screen- Statische Farbsegmente: Grün (Reku) → Gelb → Orange → Rot (Vollgas)

- Instant UI reload without restart- Skala-Striche mit Zahlenbeschriftung

- All screens and navigation buttons support both languages

- Language preference persisted in settings.json### 🚨 **Intelligentes Warn-System**



### 🎛️ **Power Gauge with Logarithmic Scaling**- **Status-Bar** auf allen Screens mit Datum, Uhrzeit, Außentemperatur

- **Kritische Fehler-Warnung**: Rote Umrandung + blinkende Meldung bei:

- Range: -50 kW (Regeneration) to +200 kW (Full throttle)  - Isolationsfehler (⚠ ISOLATION)

- Pseudo-logarithmic scaling for better resolution in normal range (0-30 kW)  - Emergency/Notfall (⚠ NOTFALL)

- Static color segments: Green (Regen) → Yellow → Orange → Red (Full throttle)  - Zell-Überladen >4.25V (⚡ ÜBERLADEN)

- Scale markings with numerical labels  - Zell-Tiefentladen <2.5V (🔋 TIEFENTLADEN)

  - Temperatur-Fehler (🌡 TEMP HOCH/❄ TEMP TIEF)

### 🚨 **Intelligent Warning System**- **Frostwarnung**: Außentemperatur <3°C wird rot markiert



- **Status Bar** on all screens with date, time, ambient temperature### 🔋 **Zellspannungs-Monitoring**

- **Critical Error Warning**: Red border + blinking message for:

  - Isolation error (⚠ ISOLATION)- Alle 88 Zellen einzeln dargestellt (4 Reihen × 22 Zellen)

  - Emergency (⚠ EMERGENCY)- Vertikale Bargraphen mit Farbcodierung:

  - Cell overcharge >4.25V (⚡ OVERCHARGED)  - Rot: >4.2V (kritisch hoch)

  - Cell deep discharge <2.5V (🔋 DEEP DISCHARGE)  - Orange: <3.0V (kritisch niedrig)

  - Temperature errors (🌡 TEMP HIGH/❄ TEMP LOW)  - Grün: 3.5-4.1V (optimal)

- **Frost Warning**: Ambient temperature <3°C marked in red  - Gelb: Grenzbereich

- Dicke rote Umrandung bei kritischen Zellen

### 🔋 **Cell Voltage Monitoring**- Min/Max/Durchschnitt/Delta-Anzeige



- All 88 cells displayed individually (4 rows × 22 cells)### 📡 **Robuste CAN-Bus Integration**

- Vertical bar graphs with color coding:

  - Red: >4.2V (critically high)- Zuverlässige Initialisierung mit Retry-Logik

  - Orange: <3.0V (critically low)- Automatisches Recovery bei CAN-Bus-Fehlern

  - Green: 3.5-4.1V (optimal)- Vollständige Dekodierung aller bekannten ThinkCity CAN-IDs

  - Yellow: Borderline range- Testmodus mit vcan0 für Entwicklung ohne Hardware

- Thick red border for critical cells

- Min/Max/Average/Delta display### 💾 **Datenlogging & Performance**



### 📡 **Robust CAN Bus Integration**- SQLite-Datenbank auf SSD mit Auto-Mount-Check

- Trip-Tracking (Start/Stop-Erkennung)

- Reliable initialization with retry logic- Selektives UI-Update (nur geänderte Werte)

- Automatic recovery from CAN bus errors- Optimiertes Rendering für geringe CPU-Last

- Complete decoding of all known ThinkCity CAN IDs

- Test mode with vcan0 for development without hardware---



### 💾 **Data Logging & Performance**## 📦 Installation



- SQLite database on SSD with auto-mount check### Voraussetzungen

- Trip tracking (start/stop detection)

- Selective UI update (only changed values)- Raspberry Pi 4B

- Optimized rendering for low CPU usage- USB-SSD (empfohlen für schnelles Booten)

- HDMI-Touchscreen (getestet mit SunFounder 10" 1280x800)

---- MCP2515 CAN-Modul (SPI)



## 📦 Installation### Schnellstart



### Prerequisites```bash

cd /home/pi

- Raspberry Pi 4Bgit clone <repo> thinkcity-dashboard-v3  # oder kopiere den Ordner

- USB SSD (recommended for fast boot)cd thinkcity-dashboard-v3

- HDMI touchscreen (tested with SunFounder 10" 1280x800)chmod +x setup.sh

- MCP2515 CAN module (SPI)./setup.sh

sudo reboot

### Quick Start```



```bashDas Setup-Skript:

cd /home/pi

git clone https://github.com/Arndt-Barop/thinkcity-dashboard.git thinkcity-dashboard-v31. Installiert alle Abhängigkeiten

cd thinkcity-dashboard-v3

chmod +x setup.sh---2. Konfiguriert MCP2515 (SPI + Device Tree Overlay)

./setup.sh

sudo reboot3. Richtet Auto-Mount für SSD ein

```

## 🖥️ Hardware-Anforderungen4. Installiert systemd-Services

The setup script:

1. Installs all dependencies5. Optimiert das System für schnellen Boot

2. Configures MCP2515 (SPI + Device Tree Overlay)

3. Sets up auto-mount for SSD### Minimum

4. Installs systemd services

5. Optimizes system for fast boot- **Raspberry Pi 4B** (2GB RAM)---



---- **SunFounder 10" HDMI Touchscreen** (1280×800)



## 🖥️ Hardware Requirements- **MCP2515 CAN-Modul** (SPI-Interface)## 🖥️ Display-Konfiguration



### Minimum- **16GB microSD-Karte** (USB-Boot empfohlen für Geschwindigkeit)

- **Raspberry Pi 4B** (2GB RAM)

- **SunFounder 10" HDMI Touchscreen** (1280×800)Das System unterstützt **drei Modi** für HDMI-Touchscreens:

- **MCP2515 CAN Module** (SPI interface)

- **16GB microSD card** (USB boot recommended for speed)### Empfohlen



### Recommended- Raspberry Pi 4B mit 4GB RAM## 📦 Installations-Optionen

- Raspberry Pi 4B with 4GB RAM

- USB 3.0 SSD (128GB+) for boot and database- USB 3.0 SSD (128GB+) für Boot und Datenbank

- Active cooling (small fan)

- High-quality 5V/3A USB-C power supply- Aktive Kühlung (kleiner Lüfter)### Option 1: Minimal X11 + Kiosk (EMPFOHLEN)



### CAN Bus Connection- Hochwertige 5V/3A USB-C Stromversorgung```bash

- MCP2515 via SPI on GPIO header

- CAN-H/CAN-L to ThinkCity OBD connectorsudo raspi-config

- 120Ω termination resistor (usually integrated in MCP2515 module)

### CAN-Bus Verbindung# → System Options → Boot → Desktop Autologin

---

- MCP2515 per SPI an GPIO-Header# → Display Options → Resolution → Wähle native Auflösung

## 🎮 Operation

- CAN-H/CAN-L an ThinkCity OBD-Stecker```

### Touch Navigation

- **Main** → Main screen (Speed, Power, SOC)- 120Ω Abschlusswiderstand (meist im MCP2515-Modul integriert)

- **Battery** → Cell voltages, Temperatures, Details

- **Cells** → Individual cell voltage bars**Service nutzt automatisch:**

- **Charge** → Charging status, Mains info, EOC

- **Raw** → Live CAN traffic---```ini

- **⚙️** → Settings (CAN, Network, Logging, Language)

Environment=QT_QPA_PLATFORM=xcb

### Keyboard Shortcuts (Debug)

- `Q` → Quit## 📦 InstallationEnvironment=DISPLAY=:0

- `F` → Fullscreen toggle

- `R` → Reset trip counter```

- `1-6` → Screen switch

### Schnellinstallation

---

**Vorteile:**

## 📊 Calculated Values

```bash- ✅ Beste Kompatibilität mit HDMI-Touchscreens

### Range (km)

```# 1. System vorbereiten- ✅ Touch funktioniert out-of-the-box

Range = (SOC / 100) × Battery_Capacity_kWh × 1000 / Average_Consumption_Wh_km

```sudo apt update && sudo apt upgrade -y- ✅ Einfache Konfiguration

- **Battery Capacity:** 24 kWh (EnerDel), calibratable

- **Average Consumption:** From trip data or default 150 Wh/km



### Consumption (kWh/100km)# 2. Projekt klonen**Nachteile:**

```

Current = (Power_kW / Speed_km_h) × 100cd /home/pi- ⚠️ Etwas langsamerer Boot (~5s mehr)

Trip = Total_kWh_consumed / Distance_km × 100

```git clone https://github.com/Arndt-Barop/thinkcity-dashboard.git thinkcity-dashboard-v3

**Only calculated at speed > 2 km/h**

cd thinkcity-dashboard-v3---

### SOH (State of Health)

Estimated from:

- Max/Min cell voltages (EnerDel)

- Number of faulty cells# 3. Installation ausführen### Option 2: Linux Framebuffer (Lite-Alternative)

- Aging curve (optionally calibratable)

chmod +x install.shEditiere `/etc/systemd/system/thinkcity-dashboard.service`:

**Currently:** Placeholder, as not directly available via CAN

./install.sh```ini

---

Environment=QT_QPA_PLATFORM=linuxfb

## 🗄️ Data Logging

# 4. Neustart```

### Automatic Trip Tracking

- **Start:** First movement after standstill (Speed > 0)sudo reboot

- **Stop:** 5 minutes standstill or ignition off

```**Vorteile:**

### Database Structure

```sql- ✅ Funktioniert ohne X11

-- drives: One entry per trip

CREATE TABLE drives (Das Installations-Skript:- ✅ Schnellerer Boot

    id INTEGER PRIMARY KEY,

    start_time TEXT,- Installiert Python 3.9+ und alle Abhängigkeiten

    end_time TEXT,

    start_soc REAL,- Konfiguriert MCP2515 CAN-Interface (Device Tree Overlay)**Nachteile:**

    end_soc REAL,

    start_odometer REAL,- Richtet systemd-Service für Auto-Start ein- ⚠️ Touch-Input benötigt ggf. manuelle Konfiguration

    end_odometer REAL,

    distance_km REAL,- Optimiert Boot-Parameter für schnellen Start- ⚠️ Nicht alle Qt-Widgets funktionieren perfekt

    avg_consumption_kwh_100km REAL,

    synced INTEGER DEFAULT 0- Konfiguriert Framebuffer und Video-Treiber

);

---

-- samples: Detailed values (every 1-5s)

CREATE TABLE samples (### Manuelle Installation

    id INTEGER PRIMARY KEY,

    drive_id INTEGER,### Option 3: EGLFS (nur für DSI-Displays)

    timestamp TEXT,

    speed REAL,<details>Nur verwenden, wenn du ein **offizielles Raspberry Pi DSI-Display** hast!

    soc REAL,

    power REAL,<summary>Klick zum Ausklappen</summary>

    voltage REAL,

    current REAL,```ini

    pack_temp REAL,

    latitude REAL,      -- NULL if no GPS```bashEnvironment=QT_QPA_PLATFORM=eglfs

    longitude REAL,

    FOREIGN KEY(drive_id) REFERENCES drives(id)# Python-Pakete installierenEnvironment=QT_QPA_EGLFS_INTEGRATION=eglfs_kms

);

```sudo apt install python3-pyqt5 python3-pip can-utils -y```



### Synchronizationpip3 install python-can

When in home WiFi (`TC_HOME_SSID`):

- Upload to MQTT/InfluxDB (`sync_data.py`)---

- Mark trips as `synced=1`

- Optional: Delete old data (> 30 days)# MCP2515 konfigurieren



---echo "dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25" | sudo tee -a /boot/config.txt## 🎮 Bedienung



## 🔧 Configurationecho "dtoverlay=spi-bcm2835" | sudo tee -a /boot/config.txt



### Environment Variables### Touch-Navigation

Set in `/etc/environment` or via systemd override:

# CAN-Interface Setup-Service- **Main** → Hauptbildschirm (Geschwindigkeit, Leistung, SOC)

```bash

# Database pathsudo cp systemd/can-setup.service /etc/systemd/system/- **Battery** → Zellspannungen, Temperaturen, Details

TC_DB_PATH=/mnt/ssd/thinkcity.db

sudo systemctl enable can-setup.service- **Charge** → Ladestatus, Mains-Info, EOC

# Home WiFi for sync

TC_HOME_SSID=MyWiFi- **Settings** → Kalibrierung, Trip-Reset, System



# MQTT (optional)# Dashboard-Service

TC_MQTT_HOST=192.168.1.10

TC_MQTT_TOPIC=thinkcitysudo cp systemd/thinkcity-dashboard.service /etc/systemd/system/### Tastatur-Shortcuts (Debug)



# InfluxDB (optional)sudo systemctl enable thinkcity-dashboard.service- `Q` → Beenden

TC_INFLUX_URL=http://192.168.1.10:8086

TC_INFLUX_TOKEN=my-token- `F` → Fullscreen Toggle

TC_INFLUX_ORG=home

TC_INFLUX_BUCKET=thinkcity# Boot-Optimierung- `R` → Trip-Counter zurücksetzen



# Battery calibrationsudo nano /boot/cmdline.txt- `1-4` → Screen-Wechsel

TC_BATTERY_CAPACITY_KWH=24.0

TC_DEFAULT_CONSUMPTION_WH_KM=150.0# Füge hinzu: sdhci.debug_quirks2=4 vt.global_cursor_default=0

```

---

### Systemd Override

```bash# Video-Treiber

sudo systemctl edit thinkcity-dashboard.service

```sudo nano /boot/config.txt## 📊 Berechnete Werte

Add:

```ini# Füge hinzu: dtoverlay=vc4-fkms-v3d

[Service]

Environment=TC_BATTERY_CAPACITY_KWH=23.5### Range (km)

Environment=TC_DEFAULT_CONSUMPTION_WH_KM=140.0

```sudo reboot```



---```Range = (SOC / 100) × Batteriekapazität_kWh × 1000 / Durchschnittsverbrauch_Wh_km



## 🐛 Troubleshooting</details>```



### Dashboard Won't Start- **Batteriekapazität:** 24 kWh (EnerDel), kalibrierbar

```bash

# Check logs---- **Durchschnittsverbrauch:** Aus Trip-Daten oder Standardwert 150 Wh/km

journalctl -u thinkcity-dashboard.service -b



# Common issues:

# 1. CAN interface missing## 🚀 Verwendung### Consumption (kWh/100km)

sudo ip link set can0 up type can bitrate 500000

```

# 2. Qt backend wrong

sudo systemctl edit thinkcity-dashboard.service### StartAktuell = (Leistung_kW / Geschwindigkeit_km_h) × 100

# Change QT_QPA_PLATFORM=linuxfb

Das Dashboard startet automatisch beim Booten. Alternativ manuell:Trip = Gesamt_kWh_verbraucht / Distanz_km × 100

# 3. Permissions

sudo chown -R pi:pi /home/pi/thinkcity-dashboard-v3```

```

```bash**Nur berechnet bei Geschwindigkeit > 2 km/h**

### Touch Not Working

```bashsudo systemctl start thinkcity-dashboard.service

# Show touchscreen devices

ls -l /dev/input/event*```### SOH (State of Health)



# For libinput (X11):Geschätzt aus:

sudo apt install xserver-xorg-input-libinput

### Navigation- Max/Min Zellspannungen (EnerDel)

# For evdev (Framebuffer):

sudo apt install tslib- **Touch-Buttons** unten: Wechsel zwischen den 5 Hauptscreens- Anzahl fehlerhafter Zellen

```

- **Swipe** (optional): Links/Rechts für Screen-Wechsel- Alterungskurve (optional kalibrierbar)

### No CAN Bus Data

```bash

# Check interface

ip -details link show can0### CAN-Bus Modi**Aktuell:** Platzhalter, da nicht direkt via CAN verfügbar



# Manual test

candump can0

#### Echtes Fahrzeug (Produktion)---

# MCP2515 connected?

dmesg | grep spi```bash

dmesg | grep can

```# Service-Datei editieren## 🗄️ Datenlogging



### Display Shows Nothingsudo nano /etc/systemd/system/thinkcity-dashboard.service

```bash

# Check HDMI output### Automatisches Trip-Tracking

vcgencmd display_power

# Setze:- **Start:** Erste Bewegung nach Standstill (Geschwindigkeit > 0)

# Set resolution

sudo raspi-configEnvironment=TC_CAN_CHANNEL=can0- **Stop:** 5 Minuten Standstill oder Zündung aus

# → Display Options → Resolution

```



---sudo systemctl daemon-reload### Datenbank-Struktur



## 🚀 Performance Tuningsudo systemctl restart thinkcity-dashboard.service```sql



### Boot Optimization (< 15s target)```-- drives: Ein Eintrag pro Fahrt

Already included in `setup.sh`:

CREATE TABLE drives (

```bash

# Disable unnecessary services#### Simulation (Test mit Replay)    id INTEGER PRIMARY KEY,

sudo systemctl disable bluetooth.service

sudo systemctl disable avahi-daemon.service```bash    start_time TEXT,

sudo systemctl mask systemd-networkd-wait-online.service

# Virtual CAN erstellen    end_time TEXT,

# Kernel parameters

# In /boot/cmdline.txt:sudo ip link add dev vcan0 type vcan    start_soc REAL,

quiet loglevel=0 logo.nologo

```sudo ip link set vcan0 up    end_soc REAL,



### RAM Optimization    start_odometer REAL,

```bash

# Reduce GPU memory (if no video)# Service auf vcan0 umstellen    end_odometer REAL,

# In /boot/config.txt:

gpu_mem=64sudo nano /etc/systemd/system/thinkcity-dashboard.service    distance_km REAL,

```

Environment=TC_CAN_CHANNEL=vcan0    avg_consumption_kwh_100km REAL,

### CPU Governor

```bash    synced INTEGER DEFAULT 0

# Performance mode for faster UI

echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor# CAN-Trace abspielen);

```

cd tools

---

python3 can_replay.py ../traces/entladen_91.log vcan0 50.0 --loop-- samples: Detaillierte Werte (alle 1-5s)

## 📁 Project Structure

```CREATE TABLE samples (

```

thinkcity-dashboard-v3/    id INTEGER PRIMARY KEY,

├── README.md                      # This file (English)

├── README_DE.md                   # German version    drive_id INTEGER,

├── setup.sh                       # Installation script

├── requirements.txt               # Python dependencies    timestamp TEXT,

│

├── dashboard.py                   # Main GUI application---    speed REAL,

├── can_decoder.py                 # CAN frame parser (extended)

├── trip_computer.py               # Range/Consumption logic    soc REAL,

├── db_manager.py                  # Database wrapper

├── translations.py                # Translation system (NEW)## 📁 Projekt-Struktur    power REAL,

│

├── main_screen.py                 # Main screen    voltage REAL,

├── battery_screen.py              # Battery details

├── charge_screen.py               # Charge screen```    current REAL,

├── cell_voltages_screen.py        # Cell voltage details

├── raw_data_screen.py             # CAN raw datathinkcity-dashboard-v3/    pack_temp REAL,

├── settings_screen.py             # Settings (NEW)

├── widgets.py                     # Reusable widgets├── README.md                      # Diese Datei    latitude REAL,      -- NULL wenn kein GPS

│

├── can_interface.py               # CAN bus management├── install.sh                     # Installations-Skript    longitude REAL,

├── systemd/

│   ├── thinkcity-dashboard.service├── requirements.txt               # Python-Abhängigkeiten    FOREIGN KEY(drive_id) REFERENCES drives(id)

│   └── can-setup.service

││);

└── tools/

    ├── can_replay.py              # CAN trace player├── dashboard.py                   # Haupt-Anwendung```

    └── trc2candump.py             # PCAN trace converter

```├── can_decoder.py                 # CAN-Frame Dekodierung



---├── can_interface.py               # CAN-Bus Verwaltung### Synchronisierung



## 📊 CAN Bus Reference├── trip_computer.py               # Range/Verbrauch BerechnungWenn im Home-WLAN (`TC_HOME_SSID`):



### Supported CAN IDs├── db_manager.py                  # SQLite Datenbank- Upload zu MQTT/InfluxDB (`sync_data.py`)



| ID (Hex) | Description | Update Rate |│- Markiere Fahrten als `synced=1`

|----------|-------------|-------------|

| 0x210 | Battery Voltage/Current/Power | 100ms |├── main_screen.py                 # Hauptbildschirm- Optional: Alte Daten löschen (> 30 Tage)

| 0x215 | SOC, Capacity, Flags | 100ms |

| 0x220 | Limits (Max V/A) | 500ms |├── battery_screen.py              # Batterie-Details

| 0x230 | Status Flags, Errors | 100ms |

| 0x264 | Drive Mode (P/N/R/D/E) | 50ms |├── charge_screen.py               # Lade-Screen---

| 0x26C | PCU Ambient Temperature | 500ms |

| 0x301-0x316 | Cell Voltages (88 cells, 4 per frame) | 1000ms |├── cell_voltages_screen.py        # Zellspannungs-Detail

| 0x4B0 | Motor Speed | 50ms |

| 0x495 | Motor Power | 50ms |├── raw_data_screen.py             # CAN-Rohdaten## 🔧 Konfiguration

| 0x5E3 | Mains (AC) Voltage/Current | 200ms |

├── widgets.py                     # Wiederverwendbare UI-Komponenten

Complete documentation: [CAN_REFERENCE.md](docs/CAN_REFERENCE.md)

│### Umgebungsvariablen

---

├── tools/Setze in `/etc/environment` oder per systemd-Override:

## 🛠️ Development

│   ├── can_replay.py              # CAN-Trace Abspieler

### Prerequisites

- Python 3.9+│   └── trc2candump.py             # PCAN-Trace Konverter```bash

- PyQt5

- python-can│# Datenbank-Pfad

- SQLite3

├── traces/                        # Beispiel CAN-TracesTC_DB_PATH=/mnt/ssd/thinkcity.db

### Development Setup

```bash│   └── entladen_91.log

# Create virtual environment

python3 -m venv venv│# Home-WLAN für Sync

source venv/bin/activate

├── systemd/TC_HOME_SSID=MeinWLAN

# Install dependencies

pip install -r requirements.txt│   ├── thinkcity-dashboard.service



# Start CAN simulator│   └── can-setup.service# MQTT (optional)

sudo ip link add dev vcan0 type vcan

sudo ip link set vcan0 up│TC_MQTT_HOST=192.168.1.10

python3 tools/can_replay.py traces/entladen_91.log vcan0 50.0 --loop

└── docs/TC_MQTT_TOPIC=thinkcity

# Start dashboard


```

    ├── CAN_REFERENCE.md           # CAN-ID Dokumentation# InfluxDB (optional)

### Tests

```bash    └── INSTALL.md                 # Detaillierte InstallationTC_INFLUX_URL=http://192.168.1.10:8086

# Test CAN decoder

python3 -m pytest tests/```TC_INFLUX_TOKEN=mein-token



# UI without CAN busTC_INFLUX_ORG=home


```---TC_INFLUX_BUCKET=thinkcity



---



## 🔮 Planned Features (GPS Preparation)## 🔧 Konfiguration# Batterie-Kalibrierung



### GPS Module (later)TC_BATTERY_CAPACITY_KWH=24.0

- **Hardware:** USB GPS (e.g. VK-162, U-blox NEO-6M)

- **Schema extended:** `latitude`, `longitude` already in DB### UmgebungsvariablenTC_DEFAULT_CONSUMPTION_WH_KM=150.0

- **Map integration:** Offline maps (OSM) for trip replay

- **Geofencing:** Automatic home detection (instead of WiFi)```



### Extended StatisticsSetze in `/etc/systemd/system/thinkcity-dashboard.service`:

- Elevation profile (slope/gradient)

- Energy recovery per trip### Systemd-Override

- Temperature correlation

- Charging curve analysis```ini```bash



---[Service]sudo systemctl edit thinkcity-dashboard.service



## 📝 License# CAN-Interface```



MIT License - Free use for private projects.Environment=TC_CAN_CHANNEL=can0          # oder vcan0 für SimulationFüge hinzu:



---```ini



## 🙏 Credits# Display[Service]



- **Original Code:** DuinoMite MMBasic (ENER_AUTORUN.BAS)Environment=QT_QPA_PLATFORM=linuxfbEnvironment=TC_BATTERY_CAPACITY_KWH=23.5

- **CAN Database:** SavvyCAN Community

- **Concept:** Arndt + GitHub CopilotEnvironment=TC_FULLSCREEN=1Environment=TC_DEFAULT_CONSUMPTION_WH_KM=140.0

- **Base:** ChatGPT version (thinkcity-dashboard-rpios-v2)

- **Development:** Arndt Barop + Claude Sonnet 3.5```



---# Datenbank



## 📞 SupportEnvironment=TC_DB_PATH=/home/pi/thinkcity-dashboard-v3/thinkcity.db---



- **Issues**: [GitHub Issues](https://github.com/Arndt-Barop/thinkcity-dashboard/issues)

- **Discussions**: [GitHub Discussions](https://github.com/Arndt-Barop/thinkcity-dashboard/discussions)

- **Wiki**: [Project Wiki](https://github.com/Arndt-Barop/thinkcity-dashboard/wiki)# Batterie-Kalibrierung## 🐛 Troubleshooting



---Environment=TC_BATTERY_CAPACITY_KWH=24.0



**Enjoy your ThinkCity Dashboard! ⚡🚗**Environment=TC_DEFAULT_CONSUMPTION_WH_KM=150.0### Dashboard startet nicht


``````bash

# Logs prüfen

### CAN-Interface Parameterjournalctl -u thinkcity-dashboard.service -b



```bash# Häufige Probleme:

# can-setup.service editieren# 1. CAN-Interface fehlt

sudo nano /etc/systemd/system/can-setup.servicesudo ip link set can0 up type can bitrate 500000



# Bitrate ändern (Standard: 500000)# 2. Qt-Backend passt nicht

ExecStart=/usr/sbin/ip link set can0 up type can bitrate 500000sudo systemctl edit thinkcity-dashboard.service

```# Ändere QT_QPA_PLATFORM=linuxfb



---# 3. Permissions

sudo chown -R pi:pi /home/pi/thinkcity-dashboard-v3

## 🐛 Troubleshooting```



### Dashboard startet nicht### Touch funktioniert nicht

```bash```bash

# Logs prüfen# Touchscreen-Devices anzeigen

journalctl -u thinkcity-dashboard.service -n 50ls -l /dev/input/event*



# Häufige Fehler:# Für libinput (X11):

# - PyQt5 fehlt: sudo apt install python3-pyqt5sudo apt install xserver-xorg-input-libinput

# - CAN-Interface fehlt: sudo systemctl start can-setup.service

# - Permissions: sudo chown -R pi:pi /home/pi/thinkcity-dashboard-v3# Für evdev (Framebuffer):

```sudo apt install tslib

```

### Kein CAN-Traffic

```bash### CAN-Bus empfängt keine Daten

# Interface Status```bash

ip -details link show can0# Interface prüfen

ip -details link show can0

# Manuell hochfahren

sudo ip link set can0 down# Manueller Test

sudo ip link set can0 up type can bitrate 500000candump can0



# Traffic testen# MCP2515 verbunden?

candump can0dmesg | grep spi

dmesg | grep can

# MCP2515 erkannt?```

dmesg | grep mcp251

dmesg | grep spi### Display zeigt nichts

``````bash

# HDMI-Output prüfen

### Touch funktioniert nichtvcgencmd display_power

```bash

# Touchscreen-Events prüfen# Auflösung setzen

evtestsudo raspi-config

# → Display Options → Resolution

# Für linuxfb Backend```

sudo apt install tslib

export TSLIB_TSDEVICE=/dev/input/event0---

```

## 🚀 Performance-Tuning

### Display-Probleme

```bash### Boot-Optimierung (< 15s Ziel)

# Auflösung prüfenBereits im `setup.sh` enthalten:

fbset```bash

# Unnötige Services deaktivieren

# HDMI-Ausgabe forcierensudo systemctl disable bluetooth.service

sudo raspi-configsudo systemctl disable avahi-daemon.service

# → Display Options → Resolution → 1280x800sudo systemctl mask systemd-networkd-wait-online.service

```

# Kernel-Parameter

Siehe [INSTALL.md](docs/INSTALL.md) für detaillierte Lösungen.# In /boot/cmdline.txt:

quiet loglevel=0 logo.nologo

---```



## 📊 CAN-Bus Referenz### RAM-Optimierung

```bash

### Unterstützte CAN-IDs# GPU-Memory reduzieren (wenn kein Video)

# In /boot/config.txt:

| ID (Hex) | Beschreibung | Update-Rate |gpu_mem=64

|----------|--------------|-------------|```

| 0x210 | Batterie Spannung/Strom/Leistung | 100ms |

| 0x215 | SOC, Kapazität, Flags | 100ms |### CPU-Governor

| 0x220 | Limits (Max V/A) | 500ms |```bash

| 0x230 | Status-Flags, Fehler | 100ms |# Performance-Mode für schnelleres UI

| 0x264 | Fahrmodus (P/N/R/D/E) | 50ms |echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

| 0x26C | PCU Ambient Temperatur | 500ms |```

| 0x301-0x316 | Zellspannungen (88 Zellen, 4 pro Frame) | 1000ms |

| 0x4B0 | Motor Geschwindigkeit | 50ms |---

| 0x495 | Motor Leistung | 50ms |

| 0x5E3 | Mains (AC) Spannung/Strom | 200ms |## 📁 Projekt-Struktur



Vollständige Dokumentation: [CAN_REFERENCE.md](docs/CAN_REFERENCE.md)```

thinkcity-dashboard-v3/

---├── README.md                      # Diese Datei

├── setup.sh                       # Installations-Skript

## 🛠️ Entwicklung├── requirements.txt               # Python-Abhängigkeiten

│

### Voraussetzungen├── dashboard.py                   # Haupt-GUI-Anwendung

- Python 3.9+├── can_decoder.py                 # CAN-Frame-Parser (erweitert)

- PyQt5├── trip_computer.py               # Range/Consumption-Logik (NEU)

- python-can├── db_manager.py                  # Datenbank-Wrapper (verbessert)

- SQLite3│

├── ui/

### Entwicklungs-Setup│   ├── main_screen.py             # Hauptbildschirm

```bash│   ├── battery_screen.py          # Batterie-Details

# Virtuelle Umgebung erstellen│   ├── charge_screen.py           # Lade-Screen

python3 -m venv venv│   ├── settings_screen.py         # Settings (NEU)

source venv/bin/activate│   └── widgets.py                 # Wiederverwendbare Widgets

│

# Abhängigkeiten installieren├── utils/

pip install -r requirements.txt│   ├── can_interface.py           # CAN-Bus-Verwaltung (robust)

│   ├── wifi_detector.py           # WLAN-Detection (NEU)

# CAN-Simulator starten│   └── logger.py                  # Logging-Config

sudo ip link add dev vcan0 type vcan│

sudo ip link set vcan0 up├── sync/

python3 tools/can_replay.py traces/entladen_91.log vcan0 50.0 --loop│   ├── mqtt_sync.py               # MQTT-Upload

│   └── influx_sync.py             # InfluxDB-Upload

# Dashboard starten│

TC_CAN_CHANNEL=vcan0 python3 dashboard.py├── systemd/

```│   ├── thinkcity-dashboard.service

│   ├── thinkcity-sync.service

### Tests│   └── thinkcity-sync.timer       # Periodischer Sync (NEU)

```bash│

# CAN-Decoder testen└── tests/

python3 -m pytest tests/    ├── test_can_decoder.py        # Unit-Tests

    └── can_simulator.py           # CAN-Bus-Simulator für Tests

# UI ohne CAN-Bus```


```---



---## 🔮 Geplante Features (GPS-Vorbereitung)



## 📝 Roadmap### GPS-Modul (später)

- **Hardware:** USB-GPS (z.B. VK-162, U-blox NEO-6M)

### v3.1 (geplant)- **Schema erweitert:** `latitude`, `longitude` bereits in DB

- [ ] GPS-Integration (USB-Modul)- **Karten-Integration:** Offline-Karten (OSM) für Trip-Replay

- [ ] Offline-Karten für Trip-Replay- **Geofencing:** Automatische Home-Detection (statt WLAN)

- [ ] MQTT/InfluxDB Export

- [ ] Web-Interface für Remote-Monitoring### Erweiterte Statistiken

- Höhenprofil (Steigung/Gefälle)

### v3.2 (Zukunft)- Energie-Rückgewinnung pro Trip

- [ ] Smartphone-App (Bluetooth-Sync)- Temperatur-Korrelation

- [ ] OTA-Updates über WLAN- Ladekurven-Analyse

- [ ] Erweiterte Statistiken und Diagramme

- [ ] Multi-Fahrzeug Support---



---## 📝 Lizenz



## 🤝 BeitragenMIT License - Freie Nutzung für private Projekte.



Contributions sind willkommen! Bitte:---

1. Fork das Repo

2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)## 🙏 Credits

3. Commit deine Änderungen (`git commit -m 'Add AmazingFeature'`)

4. Push zum Branch (`git push origin feature/AmazingFeature`)- **Original-Code:** DuinoMite MMBasic (ENER_AUTORUN.BAS)

5. Öffne einen Pull Request- **CAN-Database:** SavvyCAN Community

- **Konzept:** Arndt + GitHub Copilot

---- **Basis:** ChatGPT-Version (thinkcity-dashboard-rpios-v2)


## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

Freie Nutzung für private und kommerzielle Projekte. Keine Garantie oder Haftung.

---

## 🙏 Credits

- **Hardware-Reverse-Engineering**: ThinkCity Community
- **CAN-Database**: [DuinoMite MMBasic](https://github.com/duinomite) Original-Code
- **Entwicklung**: Arndt Barop + GitHub Copilot
- **Inspiration**: SavvyCAN, OVMS Project

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Arndt-Barop/thinkcity-dashboard/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Arndt-Barop/thinkcity-dashboard/discussions)
- **Wiki**: [Project Wiki](https://github.com/Arndt-Barop/thinkcity-dashboard/wiki)

---

**Viel Spaß mit deinem ThinkCity Dashboard! ⚡🚗**
