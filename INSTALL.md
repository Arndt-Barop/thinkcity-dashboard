# ThinkCity Dashboard v3 - Installation & Setup# ThinkCity Dashboard v3 - Installation & Setup



[🇩🇪 Deutsche Version](INSTALL_DE.md)## 📋 Voraussetzungen



## 📋 Prerequisites### Hardware

- ✅ Raspberry Pi 4B

### Hardware- ✅ USB-SSD (min. 16 GB, empfohlen)

- ✅ Raspberry Pi 4B- ✅ MCP2515 CAN-Modul (SPI, 16 MHz Quarz)

- ✅ USB SSD (min. 16 GB, recommended)- ✅ 7" HDMI Touchscreen

- ✅ MCP2515 CAN module (SPI, 16 MHz crystal)- ✅ 5V/3A Netzteil (Pi) + 12V→5V Wandler (Auto)

- ✅ 7-10" HDMI touchscreen

- ✅ 5V/3A power supply (Pi) + 12V→5V converter (car)### Software

- ✅ Raspberry Pi OS Lite (64-bit, Bookworm)

### Software- ✅ SD-Karte (min. 8 GB, nur für OS)

- ✅ Raspberry Pi OS Lite (64-bit, Bookworm)

- ✅ SD card (min. 8 GB, for OS only)---



---## 🚀 Schnellinstallation



## 🚀 Quick Installation### 1. Raspberry Pi OS installieren



### 1. Install Raspberry Pi OS```bash

# Raspberry Pi Imager verwenden

```bash# - OS: Raspberry Pi OS Lite (64-bit)

# Use Raspberry Pi Imager# - Hostname: thinkcity

# - OS: Raspberry Pi OS Lite (64-bit)# - User: pi

# - Hostname: thinkcity# - SSH aktivieren

# - User: pi# - WLAN konfigurieren (optional)

# - Enable SSH```

# - Configure WiFi (optional)

```### 2. System aktualisieren & USB-SSD vorbereiten



### 2. Update System & Prepare USB SSD```bash

# SSH Login

```bashssh pi@thinkcity.local

# SSH login

ssh pi@thinkcity.local# System Update

sudo apt update && sudo apt upgrade -y

# System update

sudo apt update && sudo apt upgrade -y# USB-SSD formatieren (ACHTUNG: Alle Daten werden gelöscht!)

sudo fdisk /dev/sda

# Format USB SSD (WARNING: All data will be deleted!)# - Neue Partition: n, p, 1, Enter, Enter

sudo fdisk /dev/sda# - Schreiben: w

# - New partition: n, p, 1, Enter, Enter

# - Write: wsudo mkfs.ext4 /dev/sda1

sudo mkdir -p /mnt/usbssd

sudo mkfs.ext4 /dev/sda1```

sudo mkdir -p /mnt/usbssd

```### 3. Dashboard installieren



### 3. Install Dashboard```bash

# Repository klonen (oder per USB kopieren)

```bashcd ~

# Clone repository (or copy via USB)git clone https://github.com/yourusername/thinkcity-dashboard-v3.git

cd ~# ODER: USB-Stick mit Dateien kopieren

git clone https://github.com/Arndt-Barop/thinkcity-dashboard.git thinkcity-dashboard-v3# sudo cp -r /media/usb/thinkcity-dashboard-v3 ~/

# OR: Copy from USB stick

# sudo cp -r /media/usb/thinkcity-dashboard-v3 ~/cd thinkcity-dashboard-v3



cd thinkcity-dashboard-v3# Installer ausführen

chmod +x setup.sh

# Run installersudo ./setup.sh

chmod +x setup.sh```

sudo ./setup.sh

```**Der Installer macht:**

- ✅ System-Pakete installieren (Python, PyQt5, CAN-Utils, X11)

**The installer does:**- ✅ Python-Dependencies installieren

- ✅ Install system packages (Python, PyQt5, CAN utils, X11)- ✅ MCP2515 SPI aktivieren (device-tree overlay)

- ✅ Install Python dependencies- ✅ USB-SSD auto-mount konfigurieren

- ✅ Enable MCP2515 SPI (device tree overlay)- ✅ Boot-Optimierungen (Bluetooth off, quiet boot)

- ✅ Configure USB SSD auto-mount- ✅ Systemd-Services installieren

- ✅ Boot optimizations (Bluetooth off, quiet boot)- ✅ Auto-Login + Auto-Start konfigurieren

- ✅ Install systemd services

- ✅ Configure auto-login + auto-start### 4. Hardware verkabeln



### 4. Hardware Wiring**MCP2515 → Raspberry Pi:**

```

**MCP2515 → Raspberry Pi:**MCP2515    Pi GPIO

```────────────────────

MCP2515    Pi GPIOVCC    →   Pin 17 (3.3V)

────────────────────GND    →   Pin 20 (GND)

VCC    →   Pin 17 (3.3V)CS     →   Pin 24 (GPIO 8, CE0)

GND    →   Pin 20 (GND)SO     →   Pin 21 (GPIO 9, MISO)

CS     →   Pin 24 (GPIO 8, CE0)SI     →   Pin 19 (GPIO 10, MOSI)

SO     →   Pin 21 (GPIO 9, MISO)SCK    →   Pin 23 (GPIO 11, SCLK)

SI     →   Pin 19 (GPIO 10, MOSI)INT    →   Pin 22 (GPIO 25)

SCK    →   Pin 23 (GPIO 11, SCLK)```

INT    →   Pin 22 (GPIO 25)

```**MCP2515 → ThinkCity CAN:**

```

**MCP2515 → ThinkCity CAN:**CAN-H  →   Pin 6 (CAN-Bus Stecker)

```CAN-L  →   Pin 14 (CAN-Bus Stecker)

CAN-H  →   Pin 6 (CAN bus connector)GND    →   Pin 4 oder 5

CAN-L  →   Pin 14 (CAN bus connector)```

GND    →   Pin 4 or 5

```**Wichtig:** 120Ω Terminierung am MCP2515!



**Important:** 120Ω termination at MCP2515!### 5. Testen



### 5. Test```bash

# Reboot

```bashsudo reboot

# Reboot

sudo reboot# Nach ~10-15 Sekunden sollte Dashboard automatisch starten



# After boot, check CAN interface# Falls Probleme: Manueller Start

ip -details link show can0./start_dashboard.sh



# Test CAN traffic# CAN-Bus testen

candump can0candump can0

```

# Check dashboard service

systemctl status thinkcity-dashboard.service---



# View logs## 🔧 Konfiguration

journalctl -u thinkcity-dashboard.service -f

```### Umgebungsvariablen



---Datei bearbeiten: `/etc/systemd/system/thinkcity-dashboard.service`



## 🔧 Manual Configuration```ini

Environment="TC_FULLSCREEN=1"          # 1=Fullscreen, 0=Fenster

### CAN Interface SetupEnvironment="TC_HIDE_CURSOR=1"         # 1=Cursor verstecken

Environment="TC_CAN_CHANNEL=can0"      # CAN-Interface

Edit `/boot/config.txt`:Environment="TC_DB_PATH=/mnt/usbssd/thinkcity.db"

```iniEnvironment="TC_BATTERY_CAPACITY_KWH=24.0"  # EnerDel Standard

# Enable SPIEnvironment="QT_QPA_PLATFORM=xcb"      # xcb|linuxfb|eglfs

dtparam=spi=on```



# MCP2515 CAN controller (8 MHz crystal)Nach Änderungen:

dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25```bash

```sudo systemctl daemon-reload

sudo systemctl restart thinkcity-dashboard

**Note:** If you have a 16 MHz crystal MCP2515:```

```ini

dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25---

```

## 📊 Display-Backend wählen

Create `/etc/systemd/system/can-setup.service`:

```ini### Option 1: Minimal X11 (EMPFOHLEN für HDMI)

[Unit]```bash

Description=CAN interface setupEnvironment="QT_QPA_PLATFORM=xcb"

After=network.target```

- ✅ Beste Kompatibilität mit HDMI

[Service]- ✅ Touch funktioniert out-of-the-box

Type=oneshot- ⚠️ ~5s längere Bootzeit

ExecStart=/usr/sbin/ip link set can0 up type can bitrate 500000- ⚠️ 50 MB mehr RAM

RemainAfterExit=yes

### Option 2: Linux Framebuffer (Alternativ)

[Install]```bash

WantedBy=multi-user.targetEnvironment="QT_QPA_PLATFORM=linuxfb"

``````

- ✅ Schneller Boot (~8s)

Enable service:- ⚠️ Touch kann Probleme machen

```bash- ⚠️ Kein Window-Management

sudo systemctl enable can-setup.service

sudo systemctl start can-setup.service### Option 3: EGLFS (NUR für DSI-Displays!)

``````bash

Environment="QT_QPA_PLATFORM=eglfs"

### USB SSD Auto-Mount```

- ✅ Beste Performance

Get UUID:- ❌ Funktioniert NICHT mit HDMI auf Pi OS Lite

```bash- ✅ Nur für offizielle DSI-Touchscreens

sudo blkid /dev/sda1

```---



Edit `/etc/fstab`:## 🛠️ Troubleshooting

```

UUID=your-uuid-here /mnt/usbssd ext4 defaults,nofail 0 2### Dashboard startet nicht

```

```bash

Test:# Logs prüfen

```bashsudo journalctl -u thinkcity-dashboard -f

sudo mount -a

df -h /mnt/usbssd# CAN-Interface prüfen

```ip link show can0

candump can0

### Dashboard Service

# X11 prüfen

Create `/etc/systemd/system/thinkcity-dashboard.service`:echo $DISPLAY

```inixdpyinfo

[Unit]```

Description=ThinkCity Dashboard

After=graphical.target can-setup.service### Kein CAN-Empfang

Wants=graphical.target

```bash

[Service]# MCP2515 Overlay prüfen

Type=simplesudo dtparam -l | grep mcp2515

User=pi

Environment=DISPLAY=:0# Sollte zeigen:

Environment=QT_QPA_PLATFORM=xcb# mcp2515  spi0-0  0x00001000

Environment=TC_CAN_CHANNEL=can0

Environment=TC_DB_PATH=/mnt/usbssd/thinkcity.db# SPI testen

WorkingDirectory=/home/pi/thinkcity-dashboard-v3ls /dev/spi*

ExecStart=/usr/bin/python3 /home/pi/thinkcity-dashboard-v3/dashboard.py# Sollte zeigen: /dev/spidev0.0

Restart=on-failure

RestartSec=5# CAN-Bus neu initialisieren

sudo ip link set can0 down

[Install]sudo ip link set can0 type can bitrate 500000

WantedBy=graphical.targetsudo ip link set can0 up

``````



Enable and start:### Touchscreen funktioniert nicht

```bash

sudo systemctl enable thinkcity-dashboard.service```bash

sudo systemctl start thinkcity-dashboard.service# Evdev Events prüfen

```sudo evtest

# Touchscreen sollte als /dev/input/eventX erscheinen

---

# Falls nicht: USB-Treiber prüfen

## 🎯 Boot Optimizationlsusb

dmesg | grep -i touch

### Fast Boot (<15s target)```



Edit `/boot/cmdline.txt`:### USB-SSD wird nicht gemountet

```

console=serial0,115200 console=tty3 root=PARTUUID=xxx rootfstype=ext4 fsck.repair=yes rootwait quiet loglevel=0 logo.nologo vt.global_cursor_default=0```bash

```# UUID prüfen

sudo blkid /dev/sda1

Edit `/boot/config.txt`:

```ini# fstab prüfen

# Disable Bluetoothcat /etc/fstab | grep usbssd

dtoverlay=disable-bt

# Manuell mounten

# GPU memory (minimal if no video)sudo mount /dev/sda1 /mnt/usbssd

gpu_mem=64

# Wenn immer noch Probleme: Rechte setzen

# Disable rainbow splashsudo chown -R pi:pi /mnt/usbssd

disable_splash=1```



# Disable warnings---

avoid_warnings=1

```## 📈 Performance-Optimierung



Disable services:### Boot-Zeit weiter reduzieren

```bash

sudo systemctl disable bluetooth.service```bash

sudo systemctl disable hciuart.service# In /boot/cmdline.txt ergänzen:

sudo systemctl disable avahi-daemon.servicequiet logo.nologo loglevel=0 console=tty3

sudo systemctl mask systemd-networkd-wait-online.service

```# Unnötige Services deaktivieren

sudo systemctl disable avahi-daemon

### Auto-Login Configurationsudo systemctl disable bluetooth

sudo systemctl disable ModemManager

```bashsudo systemctl mask systemd-networkd-wait-online.service

sudo raspi-config```

# → System Options → Boot → Desktop Autologin

```### RAM-Verbrauch reduzieren



Or manually edit `/etc/systemd/system/getty@tty1.service.d/autologin.conf`:```bash

```ini# GPU-RAM reduzieren (in /boot/config.txt)

[Service]gpu_mem=128  # Auf 64 reduzieren wenn kein Video benötigt

ExecStart=```

ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM

```---



---## 📦 Datensicherung



## 🐛 Troubleshooting### Datenbank-Export



### CAN Interface Not Found```bash

# Datenbank auf USB-Stick kopieren

```bashsudo cp /mnt/usbssd/thinkcity.db /media/usb/backup_$(date +%Y%m%d).db

# Check SPI

ls /dev/spi*# Oder per SFTP/SCP vom Laptop:

# Should show: /dev/spidev0.0  /dev/spidev0.1scp pi@thinkcity.local:/mnt/usbssd/thinkcity.db ~/backup/

```

# Check device tree

dmesg | grep mcp251### SD-Karten-Image erstellen (Windows)

# Should show: mcp251x spi0.0: MCP2515 successfully initialized

```

# Check CAN interface1. Win32DiskImager herunterladen

ip link show can02. SD-Karte in PC einlegen

```3. "Read" → Image speichern

4. Image auf zweite SD-Karte schreiben (Backup)

If missing:```

1. Verify wiring (especially INT pin)

2. Check `/boot/config.txt` for MCP2515 overlay---

3. Verify crystal frequency (8 MHz or 16 MHz)

4. Try different GPIO for INT (e.g., GPIO 24 instead of 25)## 🔄 Updates



### Touchscreen Not Working```bash

cd ~/thinkcity-dashboard-v3

```bashgit pull  # Oder neue Version per USB kopieren

# Check input devices

ls -l /dev/input/event*sudo systemctl restart thinkcity-dashboard

```

# Test touch

sudo evtest /dev/input/event0---



# For X11:## 📞 Support

sudo apt install xserver-xorg-input-libinput

Bei Problemen:

# For Framebuffer:1. Logs prüfen: `sudo journalctl -u thinkcity-dashboard`

export TSLIB_TSDEVICE=/dev/input/event02. CAN-Bus testen: `candump can0`

```3. Demo-Mode testen: `./start_dashboard.sh` (ohne CAN)



### Display Issues---



```bash## ⚙️ Entwicklung / Demo-Mode

# Check HDMI

vcgencmd display_power```bash

# Ohne CAN-Bus testen (generiert Fake-Daten)

# Force HDMI modeexport TC_FULLSCREEN=0

# In /boot/config.txt:python3 dashboard.py

hdmi_force_hotplug=1

hdmi_group=2# Einzelne Screens testen

hdmi_mode=87python3 main_screen.py

hdmi_cvt=1280 800 60 6 0 0 0python3 battery_screen.py

python3 charge_screen.py

# Check framebufferpython3 widgets.py

fbset

```# DB-Manager testen

python3 db_manager.py

### Dashboard Crashes

# CAN-Interface testen

```bashpython3 can_interface.py

# Check logs```

journalctl -u thinkcity-dashboard.service -n 100

---

# Common issues:

# 1. PyQt5 not installed**Viel Erfolg! 🚗⚡**

sudo apt install python3-pyqt5

# 2. Database permission
sudo chown -R pi:pi /mnt/usbssd

# 3. CAN interface not up
sudo systemctl restart can-setup.service
```

---

## 📁 File Locations

```
/home/pi/thinkcity-dashboard-v3/     # Dashboard code
/mnt/usbssd/thinkcity.db             # SQLite database
/etc/systemd/system/
    ├── can-setup.service            # CAN interface
    └── thinkcity-dashboard.service  # Dashboard autostart
/boot/
    ├── config.txt                   # Pi hardware config
    └── cmdline.txt                  # Boot parameters
```

---

## 🔄 Updates

```bash
cd ~/thinkcity-dashboard-v3
git pull
sudo systemctl restart thinkcity-dashboard.service
```

---

## 📞 Support

For detailed troubleshooting, see:
- [README.md](README.md) - Main documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [GitHub Issues](https://github.com/Arndt-Barop/thinkcity-dashboard/issues)

---

**Installation successful? Enjoy your dashboard! ⚡**
