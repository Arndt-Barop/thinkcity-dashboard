# DS3231 RTC-Modul - Schnellstart-Guide

## Hardware-Anschluss

**Vor dem Anschließen: Pi ausschalten!**

```
DS3231 Pin    →  Raspberry Pi 4
─────────────────────────────────
VCC           →  Pin 1  (3.3V)    [ROT]
GND           →  Pin 6  (GND)     [SCHWARZ]
SDA           →  Pin 3  (GPIO2)   [BLAU]
SCL           →  Pin 5  (GPIO3)   [GELB]
```

**WICHTIG:**
- ✅ CR2032 Batterie auf RTC-Modul einlegen
- ✅ 3.3V verwenden (NICHT 5V!)
- ✅ Kabel gut befestigen

---

## Installation (nach Anschluss)

### Methode 1: Automatisches Setup-Skript (EMPFOHLEN)

```bash
# Skript auf Pi kopieren
scp tools/setup_rtc.sh pi@10.42.0.214:~/

# Auf Pi ausführen
ssh pi@10.42.0.214
sudo ./setup_rtc.sh
```

Das Skript:
1. Installiert I2C-Tools
2. Aktiviert I2C-Interface
3. Konfiguriert DS3231 RTC-Overlay
4. Entfernt fake-hwclock
5. Installiert hwclock-sync Service
6. Setzt Zeitzone auf Europe/Berlin
7. Bietet Neustart an

### Methode 2: Manuelle Installation

```bash
# 1. I2C-Tools installieren
sudo apt-get update
sudo apt-get install -y i2c-tools

# 2. I2C aktivieren
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt

# 3. RTC-Overlay hinzufügen
echo "dtoverlay=i2c-rtc,ds3231" | sudo tee -a /boot/config.txt

# 4. fake-hwclock entfernen
sudo apt-get remove -y fake-hwclock
sudo update-rc.d -f fake-hwclock remove

# 5. Neustart
sudo reboot
```

---

## Nach dem Neustart

### 1. RTC verifizieren

```bash
# Automatische Verifikation (EMPFOHLEN)
scp tools/verify_rtc.sh pi@10.42.0.214:~/
ssh pi@10.42.0.214
sudo ./verify_rtc.sh
```

Oder manuell:

```bash
# RTC Device prüfen
ls /dev/rtc*
# Sollte zeigen: /dev/rtc0

# I2C-Bus scannen
sudo i2cdetect -y 1
# Sollte zeigen: 68 oder UU bei Adresse 0x68
```

### 2. Zeit initial setzen (EINMALIG nach Installation)

```bash
# Systemzeit (von NTP) auf RTC schreiben
sudo hwclock -w

# Prüfen
sudo hwclock -r
date
```

---

## Tägliche Nutzung

**Keine Aktion nötig!** Die RTC arbeitet automatisch:

- ✅ Boot ohne Internet → Zeit korrekt (von RTC)
- ✅ Boot mit Internet → Zeit synct via NTP, RTC wird aktualisiert
- ✅ Dashboard zeigt immer korrekte Zeit

---

## Troubleshooting

### Problem: Keine I2C-Devices (`/dev/i2c-1` fehlt)

```bash
# I2C manuell aktivieren
sudo raspi-config
# Interface Options → I2C → Yes
sudo reboot
```

### Problem: RTC-Zeit falsch

```bash
# Systemzeit auf RTC schreiben
sudo hwclock -w

# Prüfen
sudo hwclock -r
```

### Problem: `i2cdetect` zeigt nichts bei 0x68

**Mögliche Ursachen:**
1. Verkabelung falsch → Überprüfe Anschlüsse
2. Batterie leer → CR2032 ersetzen
3. RTC-Modul defekt → Modul tauschen

**Debug:**
```bash
# I2C-Module prüfen
lsmod | grep i2c

# I2C-Kernel-Modul neu laden
sudo rmmod i2c_bcm2835
sudo modprobe i2c_bcm2835

# Erneut scannen
sudo i2cdetect -y 1
```

### Problem: Zeit nach Boot falsch

```bash
# RTC-Zeit manuell auf System laden
sudo hwclock -s
date

# Ursache prüfen
timedatectl status
```

---

## Tests

### Test 1: Boot ohne Internet

```bash
# Ethernet trennen
# Pi neustarten
sudo reboot

# Nach Boot prüfen
date
timedatectl status
# Zeit sollte korrekt sein!
```

### Test 2: Zeiterhalt bei Stromausfall

```bash
# 1. Pi herunterfahren
sudo shutdown -h now

# 2. Warte 5 Minuten

# 3. Pi wieder einschalten (ohne Internet)

# 4. Prüfe Zeit
date
# Sollte korrekt sein (dank Batterie)
```

---

## Wartung

### Batterie wechseln

**Symptom:** Zeit nach Stromausfall falsch

**Anleitung:**
1. Pi ausschalten
2. Alte CR2032 entfernen
3. Neue CR2032 einlegen (+ nach oben)
4. Pi starten
5. Zeit setzen: `sudo hwclock -w`

**Batterie-Lebensdauer:** 5-8 Jahre

### RTC-Zeit aktualisieren

```bash
# Bei Sommerzeit/Winterzeit oder nach Batteriewechsel
sudo hwclock -w
```

---

## Kommandos-Übersicht

```bash
# RTC-Zeit lesen
sudo hwclock -r

# Systemzeit auf RTC schreiben
sudo hwclock -w

# RTC-Zeit auf System laden
sudo hwclock -s

# Zeit vergleichen
date && sudo hwclock -r

# Status anzeigen
timedatectl status

# I2C scannen
sudo i2cdetect -y 1
```

---

## Dateien im Projekt

- `tools/setup_rtc.sh` - Automatisches Setup-Skript
- `tools/verify_rtc.sh` - Verifikations-Skript
- `docs/RTC_INSTALLATION.md` - Detaillierte Anleitung
- `docs/RTC_QUICKSTART.md` - Diese Datei

---

## Support

Bei Problemen:
1. `sudo ./verify_rtc.sh` ausführen
2. Ausgabe prüfen
3. In `docs/RTC_INSTALLATION.md` nach Lösung suchen

**Häufigste Fehler:**
- Verkabelung falsch → Pin-Belegung prüfen
- I2C nicht aktiviert → `sudo raspi-config`
- Zeit nicht initial gesetzt → `sudo hwclock -w`
