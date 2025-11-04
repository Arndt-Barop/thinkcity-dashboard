# Umschalten zwischen Simulation und echtem CAN-Bus

## 🔄 Schnell-Übersicht

### Simulation (mit Replay)
```bash
# Service-Datei anpassen
sudo nano /etc/systemd/system/thinkcity-dashboard.service
# Setze: Environment=TC_CAN_CHANNEL=vcan0

# Änderungen aktivieren
sudo systemctl daemon-reload
sudo systemctl restart thinkcity-dashboard.service
```

### Echtes Auto (Produktion)
```bash
# Service-Datei anpassen
sudo nano /etc/systemd/system/thinkcity-dashboard.service
# Setze: Environment=TC_CAN_CHANNEL=can0

# Änderungen aktivieren
sudo systemctl daemon-reload
sudo systemctl restart thinkcity-dashboard.service
```

---

## 📝 Detaillierte Anleitung

### Service-Datei bearbeiten

Die Datei ist: `/etc/systemd/system/thinkcity-dashboard.service`

**Zeile 13** enthält die CAN-Kanal-Einstellung:

#### Für Simulation (Test mit Replay):
```ini
Environment=TC_CAN_CHANNEL=vcan0
```

#### Für echtes Auto:
```ini
Environment=TC_CAN_CHANNEL=can0
```

### Vollständige Service-Datei zur Referenz

```ini
[Unit]
Description=ThinkCity Dashboard v3
After=network.target can-setup.service
Wants=can-setup.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/thinkcity-dashboard-v3
Environment=TC_DB_PATH=/home/pi/thinkcity-dashboard-v3/thinkcity.db
Environment=QT_QPA_PLATFORM=linuxfb
Environment=TC_FULLSCREEN=1
Environment=TC_CAN_CHANNEL=vcan0    ← HIER ÄNDERN!
Environment=XDG_RUNTIME_DIR=/run/user/1000
ExecStartPre=+/bin/sh -c 'mkdir -p /run/user/1000 && chown pi:pi /run/user/1000'
ExecStartPre=+/bin/sh -c "clear > /dev/tty1 2>&1 || true"
ExecStart=/usr/bin/python3 /home/pi/thinkcity-dashboard-v3/dashboard.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Nach jeder Änderung:
```bash
sudo systemctl daemon-reload          # Konfiguration neu laden
sudo systemctl restart thinkcity-dashboard.service  # Service neu starten
```

---

## 🎬 Simulation einrichten und starten

### Schritt 1: Dateien auf den Pi kopieren

```bash
# Von deinem Arbeits-PC aus
cd /home/arndt/Dokumente/Think/thinkcity-dashboard-v3

# Tools kopieren
scp tools/can_replay.py pi@10.42.0.214:/home/pi/

# Trace-Datei kopieren (dauert ~30 Sekunden wegen 33 MB)
scp traces/entladen_91.log pi@10.42.0.214:/home/pi/
```

### Schritt 2: Virtual CAN Interface einrichten

```bash
# Auf dem Pi (via SSH)
ssh pi@10.42.0.214

# Virtual CAN erstellen
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up

# Prüfen ob vcan0 existiert
ip link show vcan0
# Sollte zeigen: "vcan0: <NOARP,UP,LOWER_UP> ..."
```

### Schritt 3: Dashboard auf vcan0 umstellen

```bash
# Auf dem Pi
sudo nano /etc/systemd/system/thinkcity-dashboard.service

# Zeile 13 ändern zu:
Environment=TC_CAN_CHANNEL=vcan0

# Speichern (Ctrl+O, Enter, Ctrl+X)

# Service neu laden
sudo systemctl daemon-reload
sudo systemctl restart thinkcity-dashboard.service
```

### Schritt 4: Replay starten

```bash
# Auf dem Pi
cd /home/pi

# Replay im Hintergrund starten
nohup python3 can_replay.py entladen_91.log vcan0 50.0 --loop > /tmp/can_replay.log 2>&1 &

# Prozess-ID merken (wird angezeigt)
# z.B.: [1] 12345
```

**Parameter erklärt:**
- `entladen_91.log` - Die Trace-Datei
- `vcan0` - Virtual CAN Interface
- `50.0` - 50x Geschwindigkeit (50x schneller als Echtzeit)
- `--loop` - Endlos wiederholen

### Schritt 5: Überprüfen ob es läuft

```bash
# CAN-Traffic anzeigen (sollte Frames zeigen)
candump vcan0

# Replay-Log anschauen
tail -f /tmp/can_replay.log

# Dashboard-Status prüfen
systemctl status thinkcity-dashboard.service
```

### Schritt 6: Replay stoppen (wenn nötig)

```bash
# Alle can_replay.py Prozesse beenden
pkill -f can_replay.py

# Oder spezifischen Prozess beenden (mit PID von vorher)
kill 12345
```

---

## 🚗 Zurück zum echten Auto wechseln

### Schritt 1: Replay stoppen
```bash
# Auf dem Pi
pkill -f can_replay.py
```

### Schritt 2: Virtual CAN deaktivieren (optional)
```bash
sudo ip link set vcan0 down
sudo ip link delete vcan0
```

### Schritt 3: Dashboard auf can0 umstellen
```bash
sudo nano /etc/systemd/system/thinkcity-dashboard.service

# Zeile 13 ändern zu:
Environment=TC_CAN_CHANNEL=can0

# Speichern und neu laden
sudo systemctl daemon-reload
sudo systemctl restart thinkcity-dashboard.service
```

### Schritt 4: Prüfen ob can0 läuft
```bash
# CAN-Interface Status
ip link show can0
# Sollte zeigen: "can0: <NOARP,UP,LOWER_UP,ECHO> ..."

# Bitrate prüfen
ip -details link show can0 | grep bitrate
# Sollte zeigen: "bitrate 500000 ..."

# Live CAN-Traffic vom Auto anzeigen
candump can0
```

---

## 🔧 Troubleshooting

### Dashboard startet nicht
```bash
# Logs anschauen
journalctl -u thinkcity-dashboard.service -n 50

# Häufige Fehler:
# - "No such device 'vcan0'" → vcan0 nicht erstellt
# - "No such device 'can0'" → MCP2515 nicht initialisiert
```

### Replay läuft nicht
```bash
# Prüfen ob vcan0 existiert
ip link show vcan0

# Prüfen ob python-can installiert ist
python3 -c "import can; print(can.__version__)"

# Log-Datei prüfen
cat /tmp/can_replay.log
```

### Keine CAN-Frames sichtbar
```bash
# vcan0 oder can0 prüfen
candump vcan0   # für Simulation
candump can0    # für echtes Auto

# Wenn nichts kommt:
# - Bei vcan0: Ist Replay gestartet?
# - Bei can0: Ist Auto eingeschaltet? Kabel angeschlossen?
```

---

## 📊 Nützliche Befehle

### Status prüfen
```bash
# Dashboard-Status
systemctl status thinkcity-dashboard.service

# CAN-Interfaces anzeigen
ip link show | grep can

# Welcher Kanal ist konfiguriert?
grep TC_CAN_CHANNEL /etc/systemd/system/thinkcity-dashboard.service

# Replay läuft?
ps aux | grep can_replay
```

### Live-Monitoring
```bash
# CAN-Traffic live anzeigen
candump vcan0   # oder can0

# Nur bestimmte IDs (z.B. SOC)
candump vcan0,301:7FF

# Mit Timestamps
candump -ta vcan0

# Statistik
canbusload vcan0@500000
```

### Performance
```bash
# Wie viele Frames wurden gesendet?
tail /tmp/can_replay.log

# CPU-Last des Replay
top -p $(pgrep -f can_replay)

# Dashboard CPU-Last
top -p $(pgrep -f "python.*dashboard")
```

---

## 💡 Tipps

1. **vcan0 nach Reboot weg?**
   - Normales Verhalten! Virtual CAN muss nach jedem Reboot neu erstellt werden
   - Für automatisches Setup: Script in `/etc/rc.local` oder systemd-Service

2. **Replay-Geschwindigkeit anpassen**
   - `1.0` = Echtzeit (48 Minuten für den kompletten Trace)
   - `10.0` = 10x schneller (4.8 Minuten)
   - `50.0` = 50x schneller (~1 Minute) - **empfohlen für Tests**
   - `100.0` = 100x schneller (~30 Sekunden)

3. **Andere Traces verwenden**
   - Einfach andere .log Datei als Parameter übergeben:
     ```bash
     python3 can_replay.py meine_andere_fahrt.log vcan0 50.0 --loop
     ```

4. **Mehrere Replays gleichzeitig?**
   - Nicht empfohlen! Nur ein Replay pro CAN-Interface

5. **Simulation beim Boot automatisch starten?**
   - Möglich mit eigenem systemd-Service
   - Besprechen wir bei Bedarf!
