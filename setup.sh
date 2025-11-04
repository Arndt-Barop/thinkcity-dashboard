#!/usr/bin/env bash
# ThinkCity Dashboard v3 - Setup Script
# Verbesserte Version mit besserer Fehlerbehandlung

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_USER="${SUDO_USER:-pi}"
PI_HOME="/home/$PI_USER"

echo "=========================================="
echo "ThinkCity Dashboard v3 - Installation"
echo "=========================================="
echo ""

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root (for sudo commands)
if [[ $EUID -eq 0 ]]; then
   error "Bitte NICHT als root ausführen! Nutze: ./setup.sh"
   exit 1
fi

# ==========================================
# 1. System-Update
# ==========================================
info "Schritt 1/9: System-Update..."
sudo apt update
sudo apt -y upgrade

# ==========================================
# 2. Basis-Pakete installieren
# ==========================================
info "Schritt 2/9: Basis-Pakete installieren..."
sudo apt -y install \
    python3-pip \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    can-utils \
    git \
    sqlite3 \
    ntpsec-ntpdate \
    wireless-tools \
    xinit \
    x11-xserver-utils \
    openbox \
    unclutter

# ==========================================
# 3. Python-Dependencies
# ==========================================
info "Schritt 3/9: Python-Pakete installieren..."
pip3 install --upgrade pip --break-system-packages || pip3 install --upgrade pip
pip3 install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages || pip3 install -r "$SCRIPT_DIR/requirements.txt"

# ==========================================
# 4. MCP2515 SPI-Konfiguration
# ==========================================
info "Schritt 4/9: MCP2515 CAN-Interface konfigurieren..."

# Find config.txt (unterschiedlich je nach Pi OS Version)
CFG="/boot/firmware/config.txt"
if [ ! -f "$CFG" ]; then
  CFG="/boot/config.txt"
fi

if [ ! -f "$CFG" ]; then
  error "config.txt nicht gefunden!"
  exit 1
fi

info "Verwende config.txt: $CFG"

# Enable SPI
if ! grep -q "^dtparam=spi=on" "$CFG"; then
  info "Aktiviere SPI..."
  echo "dtparam=spi=on" | sudo tee -a "$CFG" >/dev/null
else
  info "SPI bereits aktiviert"
fi

# MCP2515 Overlay (16MHz Quarz, INT auf GPIO25)
if ! grep -q "dtoverlay=mcp2515-can0" "$CFG"; then
  info "Füge MCP2515 Device-Tree-Overlay hinzu..."
  echo "dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25" | sudo tee -a "$CFG" >/dev/null
else
  info "MCP2515-Overlay bereits vorhanden"
fi

# SPI-BCM2835 Overlay
if ! grep -q "dtoverlay=spi-bcm2835" "$CFG"; then
  info "Füge SPI-BCM2835-Overlay hinzu..."
  echo "dtoverlay=spi-bcm2835" | sudo tee -a "$CFG" >/dev/null
else
  info "SPI-BCM2835-Overlay bereits vorhanden"
fi

# GPU Memory reduzieren (optional, spart RAM)
if ! grep -q "^gpu_mem=" "$CFG"; then
  info "Setze GPU-Memory auf 64MB..."
  echo "gpu_mem=64" | sudo tee -a "$CFG" >/dev/null
fi

# ==========================================
# 5. USB-SSD Auto-Mount
# ==========================================
info "Schritt 5/9: USB-SSD Auto-Mount konfigurieren..."

# Finde erste USB-Partition (normalerweise /dev/sda1)
USB_DEV="/dev/sda1"
MOUNT_POINT="/mnt/ssd"

if [ -b "$USB_DEV" ]; then
  info "USB-Device gefunden: $USB_DEV"
  
  sudo mkdir -p "$MOUNT_POINT"
  
  # UUID ermitteln
  USB_UUID=$(sudo blkid -s UUID -o value "$USB_DEV" || echo "")
  
  if [ -n "$USB_UUID" ]; then
    info "UUID: $USB_UUID"
    
    # fstab-Eintrag (falls noch nicht vorhanden)
    if ! grep -q "$USB_UUID" /etc/fstab; then
      info "Füge fstab-Eintrag hinzu..."
      echo "UUID=$USB_UUID $MOUNT_POINT ext4 defaults,nofail,x-systemd.device-timeout=5 0 2" | sudo tee -a /etc/fstab >/dev/null
    else
      info "fstab-Eintrag bereits vorhanden"
    fi
    
    # Sofort mounten
    sudo mount -a || warn "Mount fehlgeschlagen (evtl. schon gemountet)"
    
    # Ownership setzen
    sudo chown -R "$PI_USER:$PI_USER" "$MOUNT_POINT"
  else
    warn "Konnte UUID nicht ermitteln - überspringe fstab"
  fi
else
  warn "USB-Device $USB_DEV nicht gefunden - überspringe Auto-Mount"
  warn "Bitte USB-SSD anschließen und später manuell konfigurieren"
fi

# ==========================================
# 6. Datenbank initialisieren
# ==========================================
info "Schritt 6/9: Datenbank initialisieren..."
python3 "$SCRIPT_DIR/db_manager.py" init || warn "DB-Init fehlgeschlagen (wird beim ersten Start nachgeholt)"

# ==========================================
# 7. Boot-Optimierung
# ==========================================
info "Schritt 7/9: Boot-Optimierung..."

# Unnötige Services deaktivieren
for service in bluetooth.service hciuart.service avahi-daemon.service; do
  if systemctl is-enabled "$service" &>/dev/null; then
    info "Deaktiviere $service..."
    sudo systemctl disable "$service" 2>/dev/null || true
  fi
done

# Wait-online maskieren (beschleunigt Boot)
sudo systemctl mask systemd-networkd-wait-online.service 2>/dev/null || true

# Kernel-Parameter für schnelleren Boot
CMDLINE="/boot/cmdline.txt"
if [ ! -f "$CMDLINE" ]; then
  CMDLINE="/boot/firmware/cmdline.txt"
fi

if [ -f "$CMDLINE" ]; then
  if ! grep -q "quiet" "$CMDLINE"; then
    info "Setze Kernel-Parameter für schnelleren Boot..."
    sudo sed -i 's/$/ quiet loglevel=0 logo.nologo/' "$CMDLINE"
  fi
fi

# ==========================================
# 8. Systemd-Services installieren
# ==========================================
info "Schritt 8/9: Systemd-Services installieren..."

# Haupt-Service
sudo cp "$SCRIPT_DIR/systemd/thinkcity-dashboard.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable thinkcity-dashboard.service

info "Dashboard-Service aktiviert"

# Sync-Service (optional)
if [ -f "$SCRIPT_DIR/systemd/thinkcity-sync.service" ]; then
  sudo cp "$SCRIPT_DIR/systemd/thinkcity-sync.service" /etc/systemd/system/
  sudo cp "$SCRIPT_DIR/systemd/thinkcity-sync.timer" /etc/systemd/system/
  sudo systemctl daemon-reload
  
  info "Sync-Service installiert (noch nicht aktiviert)"
  info "Aktivierung mit: sudo systemctl enable --now thinkcity-sync.timer"
fi

# ==========================================
# 9. Auto-Login konfigurieren (für X11-Mode)
# ==========================================
info "Schritt 9/9: Auto-Login konfigurieren..."

# Minimal X11 mit Auto-Login
sudo raspi-config nonint do_boot_behaviour B4 || warn "Auto-Login konnte nicht gesetzt werden"

# Openbox-Autostart
OPENBOX_DIR="$PI_HOME/.config/openbox"
sudo -u "$PI_USER" mkdir -p "$OPENBOX_DIR"

cat > "$OPENBOX_DIR/autostart" <<'EOF'
# Deaktiviere Screensaver
xset s off
xset -dpms
xset s noblank

# Mauszeiger verstecken
unclutter -idle 0.1 &

# Dashboard starten (wird von systemd übernommen, daher auskommentiert)
# python3 /home/pi/thinkcity-dashboard-v3/dashboard.py
EOF

sudo chown "$PI_USER:$PI_USER" "$OPENBOX_DIR/autostart"

# ==========================================
# Abschluss
# ==========================================
echo ""
echo "=========================================="
echo -e "${GREEN}Installation abgeschlossen!${NC}"
echo "=========================================="
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. Reboot durchführen (für MCP2515-Overlay):"
echo "   sudo reboot"
echo ""
echo "2. Nach Reboot CAN-Interface testen:"
echo "   candump can0"
echo ""
echo "3. Dashboard-Status prüfen:"
echo "   systemctl status thinkcity-dashboard.service"
echo ""
echo "4. Logs ansehen:"
echo "   journalctl -u thinkcity-dashboard.service -f"
echo ""
echo "Optional:"
echo "- Sync-Service aktivieren:"
echo "  sudo systemctl enable --now thinkcity-sync.timer"
echo ""
echo "- Display-Mode ändern (falls nötig):"
echo "  sudo systemctl edit thinkcity-dashboard.service"
echo "  # Füge hinzu: Environment=QT_QPA_PLATFORM=linuxfb"
echo ""
echo "=========================================="
