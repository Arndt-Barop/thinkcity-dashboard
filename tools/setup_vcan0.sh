#!/bin/bash
# Setup vcan0 interface for CAN simulation

# Load vcan module
modprobe vcan 2>/dev/null || true

# Wait a moment
sleep 0.5

# Create vcan0 if not exists
ip link add dev vcan0 type vcan 2>/dev/null || true

# Bring interface up
ip link set up vcan0

echo "vcan0 ready"
