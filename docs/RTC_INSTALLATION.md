# DS3231 RTC-Modul Installation

## Hardware-Anschluss

### DS3231 Pinbelegung am Raspberry Pi 4:
```
DS3231 Pin    →  Raspberry Pi 4 Pin
─────────────────────────────────────
VCC (3.3V)    →  Pin 1  (3.3V)
GND           →  Pin 6  (GND)
SDA           →  Pin 3  (GPIO2 / SDA)
SCL           →  Pin 5  (GPIO3 / SCL)
```

**WICHTIG:** 
- ✅ Nutzt I2C-Bus (Pin 3+5) - KEIN Konflikt mit MCP2515 (SPI)
- ✅ Batterie (CR2032) auf RTC-Modul einlegen für Zeiterhalt
- ✅ 3.3V verwenden (NICHT 5V!)

---

## Software-Installation

### 1. I2C aktivieren
```bash
# I2C-Interface aktivieren
sudo raspi-config
# Navigiere zu: 3 Interface Options → I5 I2C → Yes → Finish

# Alternativ direkt:
sudo sed -i 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/config.txt
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
```

### 2. I2C-Tools installieren
```bash
sudo apt-get update
sudo apt-get install -y i2c-tools
```

### 3. RTC-Modul testen
```bash
# I2C-Devices scannen (sollte 0x68 zeigen - DS3231 Adresse)
sudo i2cdetect -y 1

# Erwartete Ausgabe:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 50: -- -- -- -- -- -- -- 57 -- -- -- -- -- -- -- -- 
# 60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --  ← DS3231
# 70: -- -- -- -- -- -- -- --
```

### 4. RTC-Kernel-Modul aktivieren
```bash
# Device-Tree-Overlay für DS3231 hinzufügen
echo "dtoverlay=i2c-rtc,ds3231" | sudo tee -a /boot/config.txt

# Fake-hwclock entfernen (nutzt dann echte RTC)
sudo apt-get remove -y fake-hwclock
sudo update-rc.d -f fake-hwclock remove

# System rebooten
sudo reboot
```

---

## Nach Neustart: RTC einrichten

### 5. RTC-Zeit initial setzen
```bash
# Prüfen ob RTC erkannt wurde
ls /dev/rtc*
# Sollte zeigen: /dev/rtc0

# Aktuelle Systemzeit (von NTP) auf RTC schreiben
sudo hwclock -w

# RTC-Zeit auslesen
sudo hwclock -r

# Vergleich: Systemzeit vs. RTC-Zeit
date && sudo hwclock -r
```

### 6. Automatische Synchronisation aktivieren
```bash
# systemd-timesyncd für RTC-Sync konfigurieren
sudo systemctl enable systemd-timesyncd
sudo systemctl start systemd-timesyncd

# Status prüfen
timedatectl status
# Sollte zeigen: "RTC time: <aktuelle Zeit>"
```

---

## Systemd-Service für RTC-Sync (optional, aber empfohlen)

Erstelle `/etc/systemd/system/hwclock-sync.service`:
```ini
[Unit]
Description=Sync hardware clock with system time
After=network-online.target systemd-timesyncd.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/hwclock --systohc
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl enable hwclock-sync.service
sudo systemctl start hwclock-sync.service
```

---

## Verifizierung

### Funktionstest:
```bash
# 1. NTP deaktivieren (simuliert "kein Internet")
sudo timedatectl set-ntp false

# 2. Systemzeit auf Fake-Wert setzen
sudo date -s "2020-01-01 12:00:00"

# 3. RTC-Zeit auslesen (sollte korrekt sein)
sudo hwclock -r

# 4. Systemzeit von RTC wiederherstellen
sudo hwclock -s

# 5. Prüfen ob Zeit korrekt
date

# 6. NTP wieder aktivieren
sudo timedatectl set-ntp true
```

### Boot-Test (wichtigster Test!):
```bash
# 1. Ethernet-Kabel trennen (kein Internet)
# 2. Pi neustarten
sudo reboot

# 3. Nach Neustart: Zeit prüfen
date
timedatectl status

# Sollte zeigen:
# - Korrekte Zeit (von RTC)
# - "RTC time: <aktuelle Zeit>"
# - "System clock synchronized: no" (weil kein Internet)
```

---

## Troubleshooting

### Problem: `UU` statt `68` bei i2cdetect
**Ursache:** RTC-Kernel-Modul bereits geladen (blockiert I2C-Adresse)
**Lösung:** Das ist OK! Bedeutet RTC funktioniert bereits.

### Problem: RTC-Zeit falsch nach Batteriewechsel
```bash
# Zeit von Systemzeit auf RTC schreiben
sudo hwclock -w
```

### Problem: I2C-Fehler "Device or resource busy"
```bash
# I2C-Module neu laden
sudo rmmod i2c_bcm2835
sudo modprobe i2c_bcm2835
```

### Problem: Zeitzone falsch
```bash
# Zeitzone setzen
sudo timedatectl set-timezone Europe/Berlin
```

---

## Dashboard-Integration

Das Dashboard liest automatisch die Systemzeit via Python `datetime.now()`.
Keine Code-Änderungen nötig - RTC wird vom System transparent genutzt!

```python
from datetime import datetime

# In widgets.py StatusBar.paintEvent():
now = datetime.now()  # Nutzt automatisch RTC-Zeit
date_str = now.strftime("%d.%m.%Y")
time_str = now.strftime("%H:%M:%S")
```

---

## Hardware-Beschaffung

**Empfohlenes Modul:**
- **DS3231 AT24C32 RTC-Modul** (~6€)
  - I2C-Interface (0x68)
  - Inklusive CR2032 Batterie-Halter
  - Temperaturkompensierter Quarz (±2ppm)
  - EEPROM AT24C32 (optional nutzbar)

**Bezugsquellen:**
- Amazon: "DS3231 RTC Modul Raspberry Pi"
- AliExpress: "DS3231 AT24C32 RTC Module"
- Reichelt/Conrad: Suche "DS3231"

**Batterie:**
- CR2032 Lithium (3V) - hält 5-8 Jahre

---

## Kompatibilität mit MCP2515

✅ **100% kompatibel** - keine Konflikte!

| Modul    | Bus  | Pins                    | Adresse/CE |
|----------|------|-------------------------|------------|
| MCP2515  | SPI  | 19,21,23,24 + INT(22)  | CE0        |
| DS3231   | I2C  | 3,5 (SDA,SCL)          | 0x68       |

Beide Module können gleichzeitig betrieben werden.

---

## Wartung

- **Batterie-Lebensdauer**: 5-8 Jahre (typisch)
- **Batterie-Check**: Wenn RTC-Zeit nach Trennung falsch
- **Genauigkeit**: ±2ppm = ~1 Minute/Jahr Abweichung
- **Sync-Empfehlung**: NTP synchronisiert RTC automatisch bei Internet-Verbindung

---

## Vorher/Nachher

### VORHER (ohne RTC):
```
Boot ohne Internet → Zeit: 01.01.1970 00:00:00
Dashboard zeigt: Falsche Zeit bis WLAN verfügbar
```

### NACHHER (mit RTC):
```
Boot ohne Internet → Zeit: 05.11.2025 15:23:45 (korrekt!)
Dashboard zeigt: Immer korrekte Zeit
```

---

## Nächste Schritte

1. ✅ DS3231-Modul bestellen (~6€)
2. ✅ CR2032 Batterie einlegen
3. ✅ An GPIO Pin 1,3,5,6 anschließen
4. ✅ I2C aktivieren (`sudo raspi-config`)
5. ✅ RTC-Overlay aktivieren (`dtoverlay=i2c-rtc,ds3231`)
6. ✅ Reboot + Zeit setzen (`sudo hwclock -w`)
7. ✅ Test ohne Internet (Boot-Test)

**Geschätzte Installationszeit:** 15-20 Minuten

---

## Weiterführende Infos

- **Datenblatt DS3231**: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf
- **Raspberry Pi I2C**: https://www.raspberrypi.com/documentation/computers/os.html#i2c
- **hwclock Manual**: `man hwclock`
