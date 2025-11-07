#!/bin/bash
# setup_can_interface.sh
# Dynamically setup CAN interface based on config.json

set -e

CONFIG_FILE="/home/pi/thinkcity-dashboard-v3/config.json"
DEFAULT_INTERFACE="can0"

# Read CAN interface from config.json
if [ -f "$CONFIG_FILE" ]; then
    CAN_INTERFACE=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('can_interface', '$DEFAULT_INTERFACE'))" 2>/dev/null || echo "$DEFAULT_INTERFACE")
else
    CAN_INTERFACE="$DEFAULT_INTERFACE"
fi

echo "Setting up CAN interface: $CAN_INTERFACE"

if [ "$CAN_INTERFACE" = "vcan0" ]; then
    # Setup virtual CAN
    echo "Loading vcan kernel module..."
    modprobe vcan 2>/dev/null || true
    
    echo "Creating vcan0 interface..."
    ip link add dev vcan0 type vcan 2>/dev/null || true
    
    echo "Bringing vcan0 up..."
    ip link set up vcan0
    
    echo "✅ vcan0 is ready"
    
elif [ "$CAN_INTERFACE" = "can0" ]; then
    # Setup hardware CAN (MCP2515)
    echo "Configuring can0 (500 kbit/s)..."
    
    # Check if interface exists
    if ! ip link show can0 &>/dev/null; then
        echo "⚠️  Warning: can0 not found. Check device tree overlay."
        exit 1
    fi
    
    # Configure bitrate
    ip link set can0 type can bitrate 500000 2>/dev/null || true
    
    # Bring interface up
    ip link set can0 up
    
    echo "✅ can0 is ready"
    
else
    echo "❌ Unknown CAN interface: $CAN_INTERFACE"
    exit 1
fi

# Show interface status
ip -details link show "$CAN_INTERFACE" || true

exit 0
