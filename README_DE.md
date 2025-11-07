# ThinkCity Dashboard v3

**Modernes PyQt5 Dashboard für Think City Elektrofahrzeuge**

**Raspberry Pi 4B + HDMI-Touchscreen + MCP2515 CAN**

Ein vollwertiges CAN-Bus Dashboard für den Raspberry Pi mit SunFounder 10" HDMI-Touchscreen und MCP2515 CAN-Interface. Entwickelt mit Claude Sonnet 3.5 für präzise CAN-Bus-Dekodierung und professionelle UI-Gestaltung.

[🇬🇧 English Version](README.md)

## ⚠️ Haftungsausschluss

**Dieses Projekt ist nicht mit Think Global AS, Electric Mobility Solutions AS oder anderen Herstellern des Think City Fahrzeugs verbunden oder von diesen autorisiert.** "Think City" bezieht sich ausschließlich auf das Elektrofahrzeugmodell. Dieses Dashboard wurde als Community-Projekt für Besitzer von Think City Fahrzeugen entwickelt.

---

## 📸 Screenshots

### Hauptbildschirm
![Hauptbildschirm](docs/images/screen1-main.png)
*Geschwindigkeit, Power-Gauge (-50 bis +200 kW), Reichweite, Verbrauch, Fahrmodus*

### Batterie-Übersicht
![Batterie-Screen](docs/images/screen2-battery.png)
*Spannungen, Ströme, Temperaturen, SOC, SOH, Status-Flags*

### Zellspannungen
![Zellspannungen-Screen](docs/images/screen3-cells.png)
*Alle 88 Zellen einzeln mit Bargraphen und Farbcodierung*

### Ladestatus
![Lade-Screen](docs/images/screen4-charge.png)
*AC/DC-Werte, Ladestrom, geschätzte Ladezeit*

### CAN-Rohdaten
![Rohdaten-Screen](docs/images/screen5-rawdata.png)
*Live CAN-Traffic mit ID-Referenztabelle*

---

![Dashboard Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204B-red)

---

## ✨ Features

### 📊 **5 Hauptscreens**

- **Haupt**: Geschwindigkeit, Power-Gauge, Reichweite, Verbrauch, Fahrmodus (P/N/R/D/E)
- **Batterie**: Spannungen, Ströme, Temperaturen, Status-Flags
- **Zellen**: Detaillierte Ansicht aller 88 Zellspannungen mit Bargraphen
- **Laden**: Ladestatus, AC/DC-Werte, Zeitschätzungen
- **Rohdaten**: Live CAN-Terminal + ID-Referenztabelle
- **Einstellungen**: Systemkonfiguration, CAN-Interface, Netzwerk, Logging, **Trace Replay**

### 🎛️ **Power-Gauge mit logarithmischer Skalierung**

- Bereich: -50 kW (Rekuperation) bis +200 kW (Vollgas)
- Pseudo-logarithmische Skalierung für bessere Auflösung im Normalbereich (0-30 kW)
- Statische Farbsegmente: Grün (Rekuperation) → Gelb → Orange → Rot (Vollgas)

### 🌍 **Zweisprachige Benutzeroberfläche (DE/EN)**

- Vollständiges Übersetzungssystem mit 150+ UI-Texten
- Sprachumschalter in den Einstellungen
- Sofortiges UI-Reload bei Sprachwechsel

### 🎨 **Professionelles UI-Design**

- Touch-optimierte Buttons (mindestens 80px Höhe)
- Modernes Flat-Design mit klarer Farbcodierung
- Status-Bar auf allen Screens mit Datum, Uhrzeit, Außentemperatur
- **Frostwarnung**: Außentemperatur <3°C wird rot markiert

### 🚨 **Intelligentes Warnsystem**

Kritische Batteriezustände lösen visuelle Warnungen aus:
- Zellunterspannung (<3,0V)
- Zellüberspannung (>4,15V)
- Hohe Temperatur (>45°C)
- Niedrige Temperatur (<5°C)
- Isolationsfehler (⚠ ISOLATION)
- Schützfehler (⚠ CONTACTOR)

### 🔋 **Zellspannungs-Überwachung**

- Alle 88 Zellen einzeln dargestellt (4 Reihen × 22 Zellen)
- Farbcodierte Bargraphen:
  - Rot: <3,0V oder >4,15V (kritisch)
  - Orange: <3,0V (kritisch niedrig)
  - Grün: 3,5-4,1V (optimal)
  - Gelb: Grenzbereich
- Dicke rote Umrandung bei kritischen Zellen
- Min/Max/Durchschnitt/Delta-Anzeige

### 📡 **Robuste CAN-Bus Integration**

- Zuverlässige Initialisierung mit Retry-Logik
- Automatisches Recovery bei CAN-Bus-Fehlern
- Vollständige Dekodierung aller bekannten ThinkCity CAN-IDs
- PCAN Trace Replay für Entwicklung/Testing (vcan0)

### 💾 **Datenlogging & Performance**

- SQLite-Datenbank auf SSD mit Auto-Mount-Check
- Trip-Tracking (Start/Stop-Erkennung)
- Selektives UI-Update (nur geänderte Werte)
- Optimiertes Rendering für geringe CPU-Last

---

## 📦 Installation

### Voraussetzungen

**Hardware:**
- Raspberry Pi 4B
- USB-SSD (empfohlen für schnelles Booten)
- HDMI-Touchscreen (getestet mit SunFounder 10" 1280x800)
- MCP2515 CAN-Modul (SPI-Interface)

**Software:**
- Raspberry Pi OS Lite (64-Bit empfohlen)
- Python 3.9+
- PyQt5, python-can, SQLite3

### Schnellstart

```bash
git clone https://github.com/Arndt-Barop/thinkcity-dashboard.git
cd thinkcity-dashboard-v3
chmod +x setup.sh
sudo ./setup.sh
```

Das Setup-Script führt aus:
1. Installation aller Abhängigkeiten
2. Konfiguration des CAN-Interface (MCP2515)
3. Einrichtung der systemd-Services
4. Touchscreen-Kalibrierung
5. Aktivierung des Auto-Starts beim Booten

Siehe [INSTALL_DE.md](INSTALL_DE.md) für detaillierte manuelle Installationsschritte.

---

## 🖥️ Hardware-Anforderungen

### Minimum
- Raspberry Pi 4B mit 2GB RAM
- 16GB microSD-Karte (USB-Boot empfohlen für Geschwindigkeit)
- 5V/2,5A USB-C Netzteil
- 7" HDMI-Touchscreen (min. 800x480)

### Empfohlen
- Raspberry Pi 4B mit 4GB RAM
- USB-SSD (128GB+) für Datenbank und schnelles Booten
- Hochwertiges 5V/3A USB-C Netzteil
- 10" HDMI-Touchscreen (1280x800)
- MCP2515 CAN-Modul mit 8MHz Quarz

### CAN-Bus Verbindung

MCP2515 an Raspberry Pi SPI anschließen:

```
MCP2515    Raspberry Pi
-------    ------------
VCC    →   Pin 2  (5V)
GND    →   Pin 6  (GND)
CS     →   Pin 24 (CE0)
SO     →   Pin 21 (MISO)
SI     →   Pin 19 (MOSI)
SCK    →   Pin 23 (SCLK)
INT    →   Pin 22 (GPIO25)
```

CAN-H und CAN-L an Fahrzeug-OBD-Port anschließen.

---

## 🎮 Bedienung

### Touch-Navigation

- **Touch-Buttons** unten: Wechsel zwischen den 5 Hauptscreens
- **Einstellungen-Button** (⚙️): Systemkonfiguration
- **Wischgesten**: Nicht implementiert (Button-basierte Navigation)

### Tastatur-Shortcuts (Debug)

- `Q`: Anwendung beenden
- `F`: Vollbild umschalten
- `R`: Bordcomputer zurücksetzen
- `1-5`: Zu Screen 1-5 wechseln

---

## 📊 Berechnete Werte

### Reichweite (km)

```
Reichweite = (SOC / 100) × Batteriekapazität_kWh × 1000 / Durchschnittsverbrauch_Wh_km
```

**Parameter:**
- **Batteriekapazität:** 24 kWh (EnerDel), kalibrierbar in Einstellungen
- **Durchschnittsverbrauch:** Berechnet aus letzten 100 Samples (rollendes Fenster)

### Momentanverbrauch (Wh/km)

```
Momentanverbrauch = (Leistung_kW / Geschwindigkeit_km_h) × 1000
```

**Nur berechnet bei Geschwindigkeit > 2 km/h**

### Bordcomputer

- Erkennt automatisch Fahrtbeginn/-ende (Zündschlüssel-Zustand)
- Erfasst Gesamtstrecke, Gesamtenergie, Durchschnittsverbrauch
- In Datenbank gespeichert (überlebt harten Shutdown)
- Manueller Reset über Einstellungsmenü

---

## 🛠️ Entwicklung

Siehe [DEVELOPMENT.md](DEVELOPMENT.md) für:
- CAN Trace Replay Setup (vcan0)
- NAS-Synchronisation
- Datenbank-Schema
- Eigene Anpassungen

### Entwicklungs-Setup

```bash
# Repository klonen
git clone https://github.com/Arndt-Barop/thinkcity-dashboard.git
cd thinkcity-dashboard-v3

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip3 install -r requirements.txt

# Dashboard mit vcan0 starten (keine Hardware nötig)
python3 dashboard.py
```

Siehe [INSTALL_DE.md](INSTALL_DE.md) für vollständige Installationsanleitung.

---

## 📁 Projekt-Struktur

```
thinkcity-dashboard-v3/
├── dashboard.py                # Hauptanwendung
├── main_screen.py              # Hauptbildschirm
├── battery_screen.py           # Batterie-Übersicht
├── cells_screen.py             # Zellspannungen
├── charge_screen.py            # Ladestatus
├── raw_screen.py               # CAN-Rohdaten
├── settings_screen.py          # Einstellungsmenü
├── widgets.py                  # Custom Widgets
├── translations.py             # Übersetzungssystem
├── db_manager.py               # Datenbank-Interface
├── trip_computer.py            # Bordcomputer-Berechnungen
├── trace_parser.py             # PCAN Trace Parser
├── trace_player.py             # CAN Trace Replay
├── test_trace_replay.py        # Trace Replay Tests
├── can_decoder.py              # CAN-Message Decoder
├── crypto_utils.py             # Passwort-Verschlüsselung
├── requirements.txt            # Python-Abhängigkeiten
├── config.json                 # Benutzer-Einstellungen
├── thinkcity.db                # SQLite-Datenbank
├── traces/                     # PCAN Trace-Dateien (.trc)
├── systemd/                    # Service-Dateien
│   ├── thinkcity-dashboard.service
│   ├── can-interface.service
│   └── can-trace-replay.service
├── docs/                       # Dokumentation
│   └── images/                 # Screenshots
└── tools/                      # Hilfsprogramme
    └── setup_vcan0.sh          # Virtual CAN Setup
```

---

## 🔧 Fehlerbehebung

### Dashboard startet nicht

```bash
# Service-Status prüfen
systemctl status thinkcity-dashboard

# Logs anzeigen
journalctl -u thinkcity-dashboard -f

# CAN-Interface testen
candump can0
```

### CAN-Bus Fehler

```bash
# CAN-Interface neu starten
sudo systemctl restart can-interface

# Kernel-Meldungen prüfen
dmesg | grep -i spi
dmesg | grep -i mcp
```

### Touch funktioniert nicht

```bash
# Touchscreen-Tools installieren
sudo apt install xinput-calibrator

# Touchscreen kalibrieren
DISPLAY=:0 xinput_calibrator
```

### Datenbank-Probleme

```bash
# Datenbank-Integrität prüfen
sqlite3 thinkcity.db "PRAGMA integrity_check;"

# Datenbank sichern
cp thinkcity.db thinkcity.db.backup

# Datenbank zurücksetzen (erstellt neues Schema)
rm thinkcity.db
python3 dashboard.py
```

---

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details.

## 🤝 Beiträge

Beiträge sind willkommen! Bitte:
1. Repository forken
2. Feature-Branch erstellen
3. Änderungen committen
4. Zum Branch pushen
5. Pull Request öffnen

## 👨‍💻 Credits

- **Entwicklung:** Arndt Barop + Claude Sonnet 3.5
- **CAN-Datenbank:** Community Reverse Engineering
- **Testing:** Think City Besitzer Community

## 📧 Kontakt

Für Fragen, Probleme oder Vorschläge:
- GitHub Issues: [thinkcity-dashboard/issues](https://github.com/Arndt-Barop/thinkcity-dashboard/issues)
- Email: [your-email@example.com]

---

**⚡ Mit ❤️ für die Think City Community entwickelt**
