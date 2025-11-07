#!/bin/bash
#
# Capture screenshots from ThinkCity Dashboard running on Pi
# Uses fbgrab to capture framebuffer directly
#

PI_HOST="pi@10.42.0.214"
REMOTE_DIR="/tmp/screenshots"
LOCAL_DIR="docs/images"

echo "=== ThinkCity Dashboard Screenshot Capture ==="
echo ""

# Check if fbgrab is installed on Pi
echo "Checking if fbgrab is installed on Pi..."
if ! sshpass -p 'raspberri' ssh $PI_HOST "which fbgrab > /dev/null 2>&1"; then
    echo "fbgrab not found, installing..."
    sshpass -p 'raspberri' ssh $PI_HOST "sudo apt-get update && sudo apt-get install -y fbgrab"
fi

# Create remote screenshot directory
echo "Creating screenshot directory on Pi..."
sshpass -p 'raspberri' ssh $PI_HOST "mkdir -p $REMOTE_DIR"

echo ""
echo "=== Starting Screenshot Capture ==="
echo "Please navigate through the dashboard screens on the Pi."
echo "Press ENTER after each screen to capture it."
echo ""

# Screen 1 - Main Screen
echo "Screen 1: Main Screen (with SOH and [Repl] indicator)"
read -p "Press ENTER when ready..."
sshpass -p 'raspberri' ssh $PI_HOST "sudo fbgrab -d /dev/fb0 $REMOTE_DIR/screen1-main.png"
echo "✓ Captured screen1-main.png"

# Screen 2 - Battery Screen
echo ""
echo "Screen 2: Battery Screen"
read -p "Press ENTER when ready..."
sshpass -p 'raspberri' ssh $PI_HOST "sudo fbgrab -d /dev/fb0 $REMOTE_DIR/screen2-battery.png"
echo "✓ Captured screen2-battery.png"

# Screen 3 - Cell Voltages Screen
echo ""
echo "Screen 3: Cell Voltages Screen"
read -p "Press ENTER when ready..."
sshpass -p 'raspberri' ssh $PI_HOST "sudo fbgrab -d /dev/fb0 $REMOTE_DIR/screen3-cells.png"
echo "✓ Captured screen3-cells.png"

# Screen 4 - Charge Screen
echo ""
echo "Screen 4: Charge Screen"
read -p "Press ENTER when ready..."
sshpass -p 'raspberri' ssh $PI_HOST "sudo fbgrab -d /dev/fb0 $REMOTE_DIR/screen4-charge.png"
echo "✓ Captured screen4-charge.png"

# Screen 5 - Raw Data Screen
echo ""
echo "Screen 5: Raw Data Screen"
read -p "Press ENTER when ready..."
sshpass -p 'raspberri' ssh $PI_HOST "sudo fbgrab -d /dev/fb0 $REMOTE_DIR/screen5-rawdata.png"
echo "✓ Captured screen5-rawdata.png"

# Screen 6 - Settings Screen (NEW - with Data Logger and SOH Reset)
echo ""
echo "Screen 6: Settings Screen (with Data Logger fields and SOH Reset)"
read -p "Press ENTER when ready..."
sshpass -p 'raspberri' ssh $PI_HOST "sudo fbgrab -d /dev/fb0 $REMOTE_DIR/screen6-settings.png"
echo "✓ Captured screen6-settings.png"

echo ""
echo "=== Downloading Screenshots ==="

# Create local directory if it doesn't exist
mkdir -p $LOCAL_DIR

# Download all screenshots
sshpass -p 'raspberri' scp $PI_HOST:$REMOTE_DIR/*.png $LOCAL_DIR/

echo ""
echo "=== Cleanup ==="
sshpass -p 'raspberri' ssh $PI_HOST "rm -rf $REMOTE_DIR"

echo ""
echo "=== Done! ==="
echo "Screenshots saved to: $LOCAL_DIR/"
ls -lh $LOCAL_DIR/*.png
