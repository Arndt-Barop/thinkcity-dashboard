#!/bin/bash
# RTC DS3231 Setup-Skript für ThinkCity Dashboard
# Installiert und konfiguriert das DS3231 RTC-Modul

set -e  # Beende bei Fehler

echo "=== DS3231 RTC Setup für ThinkCity Dashboard ==="
echo ""

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Prüfe ob als root/sudo ausgeführt
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Fehler: Bitte als root ausführen (sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}Schritt 1/6: I2C-Tools installieren${NC}"
apt-get update
apt-get install -y i2c-tools python3-smbus

echo -e "${GREEN}✓ I2C-Tools installiert${NC}"
echo ""

echo -e "${YELLOW}Schritt 2/6: I2C-Interface aktivieren${NC}"
# Prüfe ob I2C bereits aktiviert
if grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "I2C ist bereits aktiviert"
else
    echo "dtparam=i2c_arm=on" >> /boot/config.txt
    echo -e "${GREEN}✓ I2C aktiviert in /boot/config.txt${NC}"
fi

# I2C-Kernel-Modul laden (falls nicht schon geladen)
if ! lsmod | grep -q i2c_bcm2835; then
    modprobe i2c-bcm2835 || true
fi

echo ""

echo -e "${YELLOW}Schritt 3/6: DS3231 RTC-Overlay konfigurieren${NC}"
# Prüfe ob RTC-Overlay bereits vorhanden
if grep -q "dtoverlay=i2c-rtc,ds3231" /boot/config.txt; then
    echo "RTC-Overlay bereits konfiguriert"
else
    echo "dtoverlay=i2c-rtc,ds3231" >> /boot/config.txt
    echo -e "${GREEN}✓ RTC-Overlay hinzugefügt${NC}"
fi

echo ""

echo -e "${YELLOW}Schritt 4/6: Fake-hwclock entfernen${NC}"
# Fake-hwclock deaktivieren (nutzt dann echte RTC)
if systemctl is-active --quiet fake-hwclock 2>/dev/null; then
    systemctl stop fake-hwclock
    systemctl disable fake-hwclock
    echo -e "${GREEN}✓ fake-hwclock gestoppt und deaktiviert${NC}"
else
    echo "fake-hwclock ist nicht aktiv"
fi

# Paket entfernen falls installiert
if dpkg -l | grep -q fake-hwclock; then
    apt-get remove -y fake-hwclock
    update-rc.d -f fake-hwclock remove || true
    echo -e "${GREEN}✓ fake-hwclock Paket entfernt${NC}"
else
    echo "fake-hwclock Paket nicht installiert"
fi

echo ""

echo -e "${YELLOW}Schritt 5/6: hwclock-sync Service installieren${NC}"
cat > /etc/systemd/system/hwclock-sync.service << 'EOF'
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
EOF

systemctl daemon-reload
systemctl enable hwclock-sync.service
echo -e "${GREEN}✓ hwclock-sync Service installiert${NC}"

echo ""

echo -e "${YELLOW}Schritt 6/6: Zeitzone auf Europe/Berlin setzen${NC}"
timedatectl set-timezone Europe/Berlin
echo -e "${GREEN}✓ Zeitzone gesetzt${NC}"

echo ""
echo -e "${GREEN}=== Installation abgeschlossen! ===${NC}"
echo ""
echo -e "${YELLOW}WICHTIG: System muss neu gestartet werden!${NC}"
echo ""
echo "Nach dem Neustart:"
echo "  1. Prüfe ob RTC erkannt wurde: ls /dev/rtc*"
echo "  2. Scanne I2C-Bus: sudo i2cdetect -y 1"
echo "  3. Setze initial die Zeit: sudo hwclock -w"
echo "  4. Prüfe RTC-Zeit: sudo hwclock -r"
echo ""
echo "Neustart jetzt durchführen? (j/n)"
read -r response
if [[ "$response" =~ ^[Jj]$ ]]; then
    echo "System wird in 5 Sekunden neu gestartet..."
    sleep 5
    reboot
else
    echo "Bitte manuell neu starten: sudo reboot"
fi
