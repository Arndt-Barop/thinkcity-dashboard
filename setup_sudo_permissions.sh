#!/bin/bash
# Setup sudo permissions für Shutdown/Reboot ohne Passwort

echo "=== Setup sudo permissions für pi-User ==="
echo ""

# Erstelle sudoers-Datei für pi-User
SUDOERS_FILE="/etc/sudoers.d/thinkcity-dashboard"

echo "Erstelle $SUDOERS_FILE ..."

sudo tee "$SUDOERS_FILE" > /dev/null << 'EOF'
# Allow pi user to shutdown and reboot without password
pi ALL=(ALL) NOPASSWD: /sbin/shutdown
pi ALL=(ALL) NOPASSWD: /sbin/reboot

# Allow pi user to manage can-simulation service
pi ALL=(ALL) NOPASSWD: /bin/systemctl enable can-simulation
pi ALL=(ALL) NOPASSWD: /bin/systemctl disable can-simulation
pi ALL=(ALL) NOPASSWD: /bin/systemctl start can-simulation
pi ALL=(ALL) NOPASSWD: /bin/systemctl stop can-simulation
pi ALL=(ALL) NOPASSWD: /bin/systemctl restart can-simulation
pi ALL=(ALL) NOPASSWD: /bin/systemctl status can-simulation
EOF

# Setze korrekte Permissions
sudo chmod 0440 "$SUDOERS_FILE"

echo "✓ Sudoers-Datei erstellt"
echo ""
echo "Der pi-User kann jetzt ohne Passwort ausführen:"
echo "  sudo shutdown -h now"
echo "  sudo reboot"
echo "  sudo systemctl {enable|disable|start|stop|restart|status} can-simulation"
echo ""
echo "Setup abgeschlossen!"
