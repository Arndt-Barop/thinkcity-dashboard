#!/bin/bash
# install_dev_features.sh
# Installiert Entwicklungs-Features (Simulation, Settings, NAS Sync)

set -e

echo "========================================="
echo "ThinkCity Dashboard - Dev Features Setup"
echo "========================================="
echo ""

# 1. Can-Simulation Service
echo "📦 Installiere CAN-Simulation Service..."
sudo cp systemd/can-simulation.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "   ℹ️  CAN-Simulation Service installiert"
echo "   ℹ️  Aktivierung über Settings-Screen"
echo ""

# 2. NAS Sync Dependencies
echo "📦 Installiere NAS Sync Dependencies..."
sudo apt-get update
sudo apt-get install -y rsync sshpass wireless-tools

# 3. Erstelle Config-Verzeichnis
echo "📁 Erstelle Config-Verzeichnis..."
mkdir -p ~/thinkcity-dashboard-v3

# 4. Tools ausführbar machen
echo "🔧 Setze Ausführungsrechte..."
chmod +x tools/nas_sync.py

# 5. Erstelle Cron-Job für NAS Sync (optional)
echo ""
echo "📅 NAS Sync kann via Cron automatisiert werden:"
echo "   Beispiel (jede Stunde):"
echo "   0 * * * * /home/pi/thinkcity-dashboard-v3/tools/nas_sync.py"
echo ""
echo "   Oder manuell über Settings-Screen starten"
echo ""

# 6. Test
echo "✅ Installation abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "  1. Dashboard neu starten: sudo systemctl restart thinkcity-dashboard"
echo "  2. Settings-Screen öffnen (⚙️ Button)"
echo "  3. CAN-Interface wählen (can0 oder vcan0)"
echo "  4. Simulation aktivieren (optional, nur für vcan0)"
echo "  5. NAS-Einstellungen konfigurieren"
echo "  6. System neu starten für Simulation-Service"
echo ""
echo "Simulation manuell aktivieren:"
echo "  sudo systemctl enable can-simulation"
echo "  sudo systemctl start can-simulation"
echo ""
