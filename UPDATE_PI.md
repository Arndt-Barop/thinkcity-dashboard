# Pi Update-Anleitung für vcan0 Auto-Setup

## Problem
Nach dem Neustart muss vcan0 manuell mit folgendem Befehl eingerichtet werden:
```bash
sudo modprobe vcan && sudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0
```

## Lösung
Der neue `can-setup.service` liest die `config.json` und richtet automatisch das konfigurierte Interface (can0 oder vcan0) beim Boot ein.

## Update-Schritte auf dem Pi

### 1. Dateien aktualisieren
```bash
cd ~/thinkcity-dashboard-v3
git pull
```

### 2. can-setup.service installieren
```bash
sudo cp systemd/can-setup.service /etc/systemd/system/
sudo cp tools/setup_can_interface.sh /home/pi/thinkcity-dashboard-v3/tools/
sudo chmod +x /home/pi/thinkcity-dashboard-v3/tools/setup_can_interface.sh
```

### 3. thinkcity-dashboard.service aktualisieren
```bash
sudo cp systemd/thinkcity-dashboard.service /etc/systemd/system/
```

### 4. Services neu laden und aktivieren
```bash
sudo systemctl daemon-reload
sudo systemctl enable can-setup.service
sudo systemctl restart thinkcity-dashboard.service
```

### 5. Prüfen ob alles funktioniert
```bash
# Service-Status prüfen
systemctl status can-setup.service
systemctl status thinkcity-dashboard.service

# vcan0 prüfen
ip link show vcan0
```

### 6. Neustart testen
```bash
sudo reboot
```

Nach dem Neustart sollte vcan0 automatisch verfügbar sein, ohne dass du manuell modprobe/ip link ausführen musst.

## Wie es funktioniert

1. **can-setup.service** startet beim Boot (vor dem Dashboard)
2. Es führt `tools/setup_can_interface.sh` aus
3. Das Skript liest `config.json` und checkt den Wert von `can_interface`
4. Bei `"can_interface": "vcan0"`:
   - Lädt vcan Kernel-Modul
   - Erstellt vcan0 Interface
   - Bringt es hoch
5. Bei `"can_interface": "can0"`:
   - Konfiguriert Hardware-CAN mit 500 kbit/s
   - Bringt es hoch

## Alte Services (optional aufräumen)

Falls noch vorhanden, kannst du die alten Services deaktivieren:
```bash
sudo systemctl disable can-interface.service 2>/dev/null || true
sudo systemctl disable can-simulation.service 2>/dev/null || true
```

## Troubleshooting

**vcan0 wird nicht erstellt:**
```bash
# Manuell testen
sudo /home/pi/thinkcity-dashboard-v3/tools/setup_can_interface.sh

# Logs prüfen
journalctl -u can-setup.service -b
```

**config.json nicht gefunden:**
- Stelle sicher, dass `/home/pi/thinkcity-dashboard-v3/config.json` existiert
- Settings-Screen einmal öffnen und speichern erstellt die Datei

**Immer noch manuelles Setup nötig:**
- Service-Status prüfen: `systemctl status can-setup.service`
- Falls "disabled": `sudo systemctl enable can-setup.service`
- Falls "failed": Logs mit `journalctl -u can-setup.service -n 50` prüfen
