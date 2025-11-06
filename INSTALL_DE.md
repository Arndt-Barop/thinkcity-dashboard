# ThinkCity Dashboard v3 - Installation & Setup

## 📋 Voraussetzungen

### Hardware
- ✅ Raspberry Pi 4B
- ✅ USB-SSD (min. 16 GB, empfohlen)
- ✅ MCP2515 CAN-Modul (SPI, 16 MHz Quarz)
- ✅ 7" HDMI Touchscreen
- ✅ 5V/3A Netzteil (Pi) + 12V→5V Wandler (Auto)

### Software
- ✅ Raspberry Pi OS Lite (64-bit, Bookworm)
- ✅ SD-Karte (min. 8 GB, nur für OS)

---

## 🚀 Schnellinstallation

### 1. Raspberry Pi OS installieren

```bash
# Raspberry Pi Imager verwenden
# - OS: Raspberry Pi OS Lite (64-bit)
# - Hostname: thinkcity
# - User: pi
# - SSH aktivieren
# - WLAN konfigurieren (optional)
```

### 2. System aktualisieren & USB-SSD vorbereiten

```bash
# SSH Login
ssh pi@thinkcity.local

# System Update
sudo apt update && sudo apt upgrade -y

# USB-SSD formatieren (ACHTUNG: Alle Daten werden gelöscht!)
sudo fdisk /dev/sda
# - Neue Partition: n, p, 1, Enter, Enter
# - Schreiben: w

sudo mkfs.ext4 /dev/sda1
sudo mkdir -p /mnt/usbssd
```

### 3. Dashboard installieren

```bash
# Repository klonen (oder per USB kopieren)
cd ~
git clone https://github.com/yourusername/thinkcity-dashboard-v3.git
# ODER: USB-Stick mit Dateien kopieren
# sudo cp -r /media/usb/thinkcity-dashboard-v3 ~/

cd thinkcity-dashboard-v3

# Installer ausführen
chmod +x setup.sh
sudo ./setup.sh
```

**Der Installer macht:**
- ✅ System-Pakete installieren (Python, PyQt5, CAN-Utils, X11)
- ✅ Python-Dependencies installieren
- ✅ MCP2515 SPI aktivieren (device-tree overlay)
- ✅ USB-SSD auto-mount konfigurieren
- ✅ Boot-Optimierungen (Bluetooth off, quiet boot)
- ✅ Systemd-Services installieren
- ✅ Auto-Login + Auto-Start konfigurieren

### 4. Hardware verkabeln

**MCP2515 → Raspberry Pi:**
```
MCP2515    Pi GPIO
────────────────────
VCC    →   Pin 17 (3.3V)
GND    →   Pin 20 (GND)
CS     →   Pin 24 (GPIO 8, CE0)
SO     →   Pin 21 (GPIO 9, MISO)
SI     →   Pin 19 (GPIO 10, MOSI)
SCK    →   Pin 23 (GPIO 11, SCLK)
INT    →   Pin 22 (GPIO 25)
```

**MCP2515 → ThinkCity CAN:**
```
CAN-H  →   Pin 6 (CAN-Bus Stecker)
CAN-L  →   Pin 14 (CAN-Bus Stecker)
GND    →   Pin 4 oder 5
```

**Wichtig:** 120Ω Terminierung am MCP2515!

### 5. Testen

```bash
# Reboot
sudo reboot

# Nach ~10-15 Sekunden sollte Dashboard automatisch starten

# Falls Probleme: Manueller Start
./start_dashboard.sh

# CAN-Bus testen
candump can0
```

---

## 🔧 Konfiguration

### Umgebungsvariablen

Datei bearbeiten: `/etc/systemd/system/thinkcity-dashboard.service`

```ini
Environment="TC_FULLSCREEN=1"          # 1=Fullscreen, 0=Fenster
Environment="TC_HIDE_CURSOR=1"         # 1=Cursor verstecken
Environment="TC_CAN_CHANNEL=can0"      # CAN-Interface
Environment="TC_DB_PATH=/mnt/usbssd/thinkcity.db"
Environment="TC_BATTERY_CAPACITY_KWH=24.0"  # EnerDel Standard
Environment="QT_QPA_PLATFORM=xcb"      # xcb|linuxfb|eglfs
```

Nach Änderungen:
```bash
sudo systemctl daemon-reload
sudo systemctl restart thinkcity-dashboard
```

---

## 📊 Display-Backend wählen

### Option 1: Minimal X11 (EMPFOHLEN für HDMI)
```bash
Environment="QT_QPA_PLATFORM=xcb"
```
- ✅ Beste Kompatibilität mit HDMI
- ✅ Touch funktioniert out-of-the-box
- ⚠️ ~5s längere Bootzeit
- ⚠️ 50 MB mehr RAM

### Option 2: Linux Framebuffer (Alternativ)
```bash
Environment="QT_QPA_PLATFORM=linuxfb"
```
- ✅ Schneller Boot (~8s)
- ⚠️ Touch kann Probleme machen
- ⚠️ Kein Window-Management

### Option 3: EGLFS (NUR für DSI-Displays!)
```bash
Environment="QT_QPA_PLATFORM=eglfs"
```
- ✅ Beste Performance
- ❌ Funktioniert NICHT mit HDMI auf Pi OS Lite
- ✅ Nur für offizielle DSI-Touchscreens

---

## 🛠️ Troubleshooting

### Dashboard startet nicht

```bash
# Logs prüfen
sudo journalctl -u thinkcity-dashboard -f

# CAN-Interface prüfen
ip link show can0
candump can0

# X11 prüfen
echo $DISPLAY
xdpyinfo
```

### Kein CAN-Empfang

```bash
# MCP2515 Overlay prüfen
sudo dtparam -l | grep mcp2515

# Sollte zeigen:
# mcp2515  spi0-0  0x00001000

# SPI testen
ls /dev/spi*
# Sollte zeigen: /dev/spidev0.0

# CAN-Bus neu initialisieren
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up
```

### Touchscreen funktioniert nicht

```bash
# Evdev Events prüfen
sudo evtest
# Touchscreen sollte als /dev/input/eventX erscheinen

# Falls nicht: USB-Treiber prüfen
lsusb
dmesg | grep -i touch
```

### USB-SSD wird nicht gemountet

```bash
# UUID prüfen
sudo blkid /dev/sda1

# fstab prüfen
cat /etc/fstab | grep usbssd

# Manuell mounten
sudo mount /dev/sda1 /mnt/usbssd

# Wenn immer noch Probleme: Rechte setzen
sudo chown -R pi:pi /mnt/usbssd
```

---

## 📈 Performance-Optimierung

### Boot-Zeit weiter reduzieren

```bash
# In /boot/cmdline.txt ergänzen:
quiet logo.nologo loglevel=0 console=tty3

# Unnötige Services deaktivieren
sudo systemctl disable avahi-daemon
sudo systemctl disable bluetooth
sudo systemctl disable ModemManager
sudo systemctl mask systemd-networkd-wait-online.service
```

### RAM-Verbrauch reduzieren

```bash
# GPU-RAM reduzieren (in /boot/config.txt)
gpu_mem=128  # Auf 64 reduzieren wenn kein Video benötigt
```

---

## 📦 Datensicherung

### Datenbank-Export

```bash
# Datenbank auf USB-Stick kopieren
sudo cp /mnt/usbssd/thinkcity.db /media/usb/backup_$(date +%Y%m%d).db

# Oder per SFTP/SCP vom Laptop:
scp pi@thinkcity.local:/mnt/usbssd/thinkcity.db ~/backup/
```

### SD-Karten-Image erstellen (Windows)

```
1. Win32DiskImager herunterladen
2. SD-Karte in PC einlegen
3. "Read" → Image speichern
4. Image auf zweite SD-Karte schreiben (Backup)
```

---

## 🔄 Updates

```bash
cd ~/thinkcity-dashboard-v3
git pull  # Oder neue Version per USB kopieren

sudo systemctl restart thinkcity-dashboard
```

---

## 📞 Support

Bei Problemen:
1. Logs prüfen: `sudo journalctl -u thinkcity-dashboard`
2. CAN-Bus testen: `candump can0`

---


```bash
# Ohne CAN-Bus testen (generiert Fake-Daten)
export TC_FULLSCREEN=0
python3 dashboard.py

# Einzelne Screens testen
python3 main_screen.py
python3 battery_screen.py
python3 charge_screen.py
python3 widgets.py

# DB-Manager testen
python3 db_manager.py

# CAN-Interface testen
python3 can_interface.py
```

---

**Viel Erfolg! 🚗⚡**
