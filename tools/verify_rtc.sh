#!/bin/bash
# RTC Verifikations-Skript
# Prüft ob DS3231 RTC korrekt funktioniert

set -e

echo "=== DS3231 RTC Verifikation ==="
echo ""

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check 1: RTC Device vorhanden
echo -n "1. RTC Device vorhanden... "
if [ -e /dev/rtc0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ /dev/rtc0 nicht gefunden${NC}"
    echo "   Lösung: sudo reboot nach RTC-Installation"
    exit 1
fi

# Check 2: I2C-Bus aktiv
echo -n "2. I2C-Bus aktiv... "
if [ -e /dev/i2c-1 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ /dev/i2c-1 nicht gefunden${NC}"
    echo "   Lösung: sudo raspi-config -> Interface Options -> I2C -> Enable"
    exit 1
fi

# Check 3: DS3231 auf I2C erkennbar
echo -n "3. DS3231 auf I2C-Bus... "
if command -v i2cdetect >/dev/null 2>&1; then
    # Suche nach 0x68 (DS3231) oder UU (bereits vom Kernel verwendet)
    i2c_output=$(sudo i2cdetect -y 1 2>/dev/null | grep -E "68|UU" || true)
    if [ -n "$i2c_output" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ DS3231 nicht auf Adresse 0x68 gefunden${NC}"
        echo "   Lösung: Überprüfe Verkabelung (VCC, GND, SDA, SCL)"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ i2cdetect nicht installiert (skip)${NC}"
fi

# Check 4: RTC-Kernel-Modul geladen
echo -n "4. RTC-Kernel-Modul... "
if lsmod | grep -q rtc_ds1307; then
    echo -e "${GREEN}✓ rtc_ds1307 geladen${NC}"
else
    echo -e "${YELLOW}⚠ rtc_ds1307 nicht geladen${NC}"
    echo "   Info: Wird beim Boot geladen durch dtoverlay=i2c-rtc,ds3231"
fi

# Check 5: hwclock funktioniert
echo -n "5. hwclock lesbar... "
if sudo hwclock -r >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    rtc_time=$(sudo hwclock -r)
    echo "   RTC-Zeit: $rtc_time"
else
    echo -e "${RED}✗ hwclock kann RTC nicht lesen${NC}"
    exit 1
fi

# Check 6: Zeitvergleich System vs RTC
echo -n "6. Zeit-Synchronisation... "
system_time=$(date +%s)
rtc_time=$(sudo hwclock -r --utc | date -f - +%s 2>/dev/null || echo "0")

if [ "$rtc_time" != "0" ]; then
    time_diff=$((system_time - rtc_time))
    if [ ${time_diff#-} -lt 5 ]; then  # Absoluter Wert < 5 Sekunden
        echo -e "${GREEN}✓ Abweichung: ${time_diff}s${NC}"
    else
        echo -e "${YELLOW}⚠ Abweichung: ${time_diff}s${NC}"
        echo "   Tipp: sudo hwclock -w (schreibt Systemzeit auf RTC)"
    fi
else
    echo -e "${YELLOW}⚠ Konnte nicht vergleichen${NC}"
fi

# Check 7: Zeitzone
echo -n "7. Zeitzone... "
current_tz=$(timedatectl show -p Timezone --value)
if [ "$current_tz" = "Europe/Berlin" ]; then
    echo -e "${GREEN}✓ $current_tz${NC}"
else
    echo -e "${YELLOW}⚠ $current_tz (empfohlen: Europe/Berlin)${NC}"
    echo "   Tipp: sudo timedatectl set-timezone Europe/Berlin"
fi

# Check 8: Boot-Config
echo -n "8. Boot-Konfiguration... "
if grep -q "dtoverlay=i2c-rtc,ds3231" /boot/config.txt; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ dtoverlay=i2c-rtc,ds3231 fehlt in /boot/config.txt${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Alle Checks bestanden! ===${NC}"
echo ""
echo "RTC-Status:"
echo "─────────────────────────────────────────"
timedatectl status | grep -E "Local time|RTC time|Time zone"
echo ""
echo "Nächste Schritte:"
echo "  • Falls RTC-Zeit falsch: sudo hwclock -w"
echo "  • Boot-Test: sudo reboot (ohne Netzwerk)"
echo "  • Nach Boot: Zeit sollte korrekt sein"
