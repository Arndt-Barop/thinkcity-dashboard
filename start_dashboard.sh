#!/bin/bash
# start_dashboard.sh
# Wrapper-Script zum manuellen Starten (ohne systemd)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== ThinkCity Dashboard v3 Starter ===${NC}\n"

# 1. CAN-Interface prüfen
echo -e "${YELLOW}[1/4]${NC} Checking CAN interface..."
if ip link show can0 &>/dev/null; then
    echo "  ✓ can0 exists"
    
    # Status prüfen
    if ip link show can0 | grep -q "UP"; then
        echo "  ✓ can0 is UP"
    else
        echo "  ⚠ can0 is DOWN, bringing up..."
        sudo ip link set can0 type can bitrate 500000
        sudo ip link set can0 up
        echo "  ✓ can0 configured"
    fi
else
    echo -e "  ${RED}✗ can0 not found!${NC}"
    echo "  Please configure CAN interface or use vcan0 for testing"
    exit 1
fi

# 2. USB-SSD Mount prüfen
echo -e "\n${YELLOW}[2/4]${NC} Checking USB-SSD mount..."
if mountpoint -q /mnt/usbssd; then
    echo "  ✓ /mnt/usbssd mounted"
    export TC_DB_PATH="/mnt/usbssd/thinkcity.db"
else
    echo "  ⚠ /mnt/usbssd not mounted, using /tmp"
    export TC_DB_PATH="/tmp/thinkcity.db"
fi

# 3. X11 Server prüfen
echo -e "\n${YELLOW}[3/4]${NC} Checking X11..."
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
    echo "  ⚠ DISPLAY not set, using :0"
fi

if xdpyinfo &>/dev/null; then
    echo "  ✓ X11 server running on $DISPLAY"
else
    echo -e "  ${RED}✗ X11 server not running!${NC}"
    echo "  Start X11 first with: startx"
    exit 1
fi

# 4. Umgebungsvariablen
echo -e "\n${YELLOW}[4/4]${NC} Setting environment..."
export QT_QPA_PLATFORM=xcb
export TC_FULLSCREEN=1
export TC_HIDE_CURSOR=1
export TC_CAN_CHANNEL=can0
export TC_BATTERY_CAPACITY_KWH=24.0

echo "  QT_QPA_PLATFORM=$QT_QPA_PLATFORM"
echo "  TC_DB_PATH=$TC_DB_PATH"
echo "  TC_CAN_CHANNEL=$TC_CAN_CHANNEL"

# Start
echo -e "\n${GREEN}Starting dashboard...${NC}\n"
python3 "$SCRIPT_DIR/dashboard.py"
