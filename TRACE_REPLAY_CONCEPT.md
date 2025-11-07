# Trace Replay System - Konzept

## Übersicht

Das Trace-Replay-System ermöglicht das Abspielen aufgezeichneter PCAN-Traces auf einem virtuellen CAN-Bus (vcan0) für Tests ohne echtes Fahrzeug.

## Dateiformat: PCAN-View (.trc)

### Format-Beispiel:
```
;$FILEVERSION=1.1
;$STARTTIME=43809.2974678819
;   Start time: 10.12.2019 07:08:21.225.0
;---+--   ----+----  --+--  ----+---  +  -+ -- -- -- -- -- -- --
     1)         2.1  Rx         0251  8  40 00 00 00 00 00 00 00 
     2)        11.4  Rx         0460  8  03 E0 00 00 00 00 00 00 
```

### Struktur:
- **Zeile 1-13**: Header mit Metadaten (beginnen mit `;`)
- **Datenzeilen**: `Nummer) Zeit_ms Rx/Tx CAN-ID Länge Daten...`
  - Nummer: Fortlaufend
  - Zeit: Millisekunden ab Start
  - Richtung: Rx (empfangen) oder Tx (gesendet)
  - CAN-ID: Hexadezimal (z.B. 0251 = 0x251)
  - Länge: Anzahl Datenbytes (1-8)
  - Daten: Hex bytes, space-separated

## Architektur

### Komponenten:

1. **trace_parser.py** - Parser für PCAN .trc Dateien
   - Liest .trc Datei
   - Überspringt Kommentare
   - Parsed CAN-Messages
   - Gibt Liste von (timestamp_ms, can_id, data) zurück

2. **trace_player.py** - Replay Engine
   - Lädt Trace via Parser
   - Spielt Messages auf vcan0 ab
   - Respektiert Original-Timing
   - Endlos-Loop möglich
   - Pause/Resume/Stop Steuerung

3. **Settings-Screen Integration**
   - Trace-Datei Auswahl (Dropdown)
   - Replay-Steuerung (Start/Stop)
   - Loop-Option
   - Status-Anzeige

4. **systemd Service Update**
   - can-simulation.service → can-replay.service
   - Verwendet trace_player.py
   - Konfigurierbare Trace-Datei

## User Workflow

### 1. Trace-Dateien bereitstellen
```bash
# Benutzer kopiert Traces auf Pi
scp *.trc pi@thinkcity:/home/pi/thinkcity-dashboard-v3/traces/
```

### 2. Im Settings-Menü
- CAN-Interface: `vcan0` wählen
- Trace-Datei: Dropdown mit allen .trc Dateien aus `~/traces/`
- "Trace beim Boot abspielen" aktivieren
- Optional: "Endlos-Loop" aktivieren
- Speichern

### 3. Automatischer Start
- Service startet vcan0
- Lädt gewählten Trace
- Spielt CAN-Messages ab
- Dashboard empfängt und decodiert

## Implementation Plan

### Phase 1: Parser & Player (Commit 1-3)
- [ ] Commit 1: trace_parser.py erstellen
- [ ] Commit 2: trace_player.py erstellen  
- [ ] Commit 3: Standalone-Test script

### Phase 2: Settings Integration (Commit 4-6)
- [ ] Commit 4: Trace-Dropdown in Settings
- [ ] Commit 5: Replay-Steuerung UI
- [ ] Commit 6: Config speichern/laden

### Phase 3: Service Integration (Commit 7-8)
- [ ] Commit 7: can-simulation → can-replay Service
- [ ] Commit 8: Systemd service file update

### Phase 4: Documentation (Commit 9)
- [ ] Commit 9: README & Anleitung

## Technische Details

### Trace Parser
```python
class PCANTraceParser:
    def parse_file(self, filepath):
        # Returns: List[(timestamp_ms, can_id, data_bytes)]
        pass
```

### Trace Player
```python
class TracePlayer:
    def __init__(self, can_channel='vcan0'):
        self.bus = can.Bus(channel=can_channel, bustype='socketcan')
    
    def play_trace(self, trace_data, loop=False):
        # Spielt Trace mit korrektem Timing
        pass
```

### Settings Integration
```python
# In settings_screen.py
self.trace_dropdown = QComboBox()
self.trace_dropdown.addItems(self._scan_traces())

def _scan_traces(self):
    traces_dir = os.path.expanduser("~/thinkcity-dashboard-v3/traces")
    return [f for f in os.listdir(traces_dir) if f.endswith('.trc')]
```

## Vorteile gegenüber Demo-Mode

✅ **Realistische Daten**: Echte CAN-Nachrichten vom Fahrzeug
✅ **Reproduzierbar**: Immer gleiche Sequenz
✅ **Testfälle**: Spezifische Szenarien (Laden, Entladen, etc.)
✅ **Timing**: Original-Timing der Messages
✅ **Vollständig**: Alle CAN-IDs inkl. seltener Messages

## Beispiel-Traces

Vorhanden in `AKKU/191210_PCAN-Traces/`:
1. `191210_Arndt_Think_Entladen_ab_91_procent.trc` (860k Zeilen)
2. `191210_Arndt_Think_Laden_ab_82_procent.trc` (1M Zeilen)
3. `191210_Arndt_Think_Laden_ab_91_procent.trc` (33k Zeilen)

## Nächste Schritte

1. Trace-Parser implementieren
2. Trace-Player implementieren
3. Settings-Integration
4. Service-Update
5. Testing mit allen 3 Traces
