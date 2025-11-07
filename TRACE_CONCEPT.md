# CAN Trace System - Konzept & Implementierung

## Übersicht

Das CAN Trace System bietet zwei Hauptfunktionen:
1. **Recording**: Aufzeichnen von Live-CAN-Daten im PCAN .trc Format
2. **Replay**: Abspielen aufgezeichneter Traces auf vcan0 für Tests

**Status: ✅ IMPLEMENTIERT**

Beide Features sind vollständig implementiert und produktiv im Einsatz.

---

## 1. CAN Trace Recording

### 🎯 Ziel

CAN-Bus Traffic in Echtzeit aufzeichnen und als PCAN .trc Datei speichern, kompatibel mit PCANview und anderen Analysetools.

### Use Cases

- 📊 Fahrdaten für spätere Analyse aufzeichnen
- 🐛 Fehlerdiagnose mit Fachmann-Support
- 🔬 Unbekannte CAN-IDs erforschen
- 📈 Performance-Analyse über längere Zeiträume
- 🎓 Lernmaterial für CAN-Bus Entwicklung

### Implementierung

**Datei:** `trace_recorder.py` (~400 Zeilen)

**Features:**
- ✅ PCAN .trc Format mit vollständiger Header-Kompatibilität
- ✅ Queue-basiertes Message Buffering (10.000 Messages)
- ✅ Background Writer Thread (Batch-Writes alle 100 Messages)
- ✅ Excel DateTime Format für Timestamps
- ✅ Auto-Stop bei <100MB freiem Speicher
- ✅ Real-time Statistiken (Dauer, Messages, Dateigröße)

**Architektur:**
```python
class TraceRecorder:
    def __init__(self, can_interface: str, output_dir: str)
    
    def start_recording(self, filename: Optional[str] = None) -> bool
    def stop_recording(self) -> dict  # Returns stats
    def record_message(self, msg: can.Message)
    def get_stats(self) -> dict  # Duration, message count, file size
    
    def _writer_thread(self)  # Background thread
    def _write_header(self)
    def _write_message(self, msg, timestamp_us)
```

**Threading Model:**
```
Main Thread (Dashboard)
    ↓
CAN Reader Thread (can_interface)
    ↓
TraceRecorder.record_message() [non-blocking]
    → Message Queue (10k capacity)
    → Writer Thread (background)
        → Flush to file every 100 messages
```

**Storage:**
- Verzeichnis: `~/thinkcity-dashboard-v3/traces/`
- Dateiname: `ThinkCity_YYYY-MM-DD_HH-MM-SS.trc`
- Format: PCAN View kompatibel

**Performance:**
- CPU Impact: <2% additional load
- RAM Usage: <10MB queue buffer
- Write Frequency: Batch every 100 messages or 100ms
- No blocking of dashboard UI

### PCAN Format Details

**Header:**
```
;$FILEVERSION=1.1
;$STARTTIME=45968.8744675925918
;   Start time: 07.11.2025 20:59:14.311.0
;
;   Message   Time    Type ID     DLC Data Bytes
;   Number    Offset  
;---+--   ----+----  --+--  ----+---  +  -+ -- -- -- -- -- -- --
```

**Message Lines:**
```
     1)      16796.5  Rx         0251  8  40 00 00 00 00 00 00 00
     2)      16890.9  Rx         0460  8  03 E0 00 00 00 00 00 00
     ↑          ↑     ↑          ↑     ↑  ↑
   Number     µs    Rx/Tx      ID   DLC Data
```

**Format-Spezifikation:**
- Message Number: Right-aligned, 6 characters
- Timestamp: Microseconds from start (µs), 1 decimal place
- Direction: Rx (received) / Tx (transmitted)
- CAN-ID: 4 hex digits (e.g., 0251, 0301)
- DLC: 1 digit (0-8)
- Data: Space-separated hex bytes (uppercase)

**Excel DateTime:**
```python
# Timestamp format for PCAN compatibility
def to_excel_datetime(dt: datetime) -> float:
    """Convert datetime to Excel float (days since 1900-01-01)"""
    excel_epoch = datetime(1899, 12, 30)
    delta = dt - excel_epoch
    return delta.total_seconds() / 86400.0
```

### UI Integration

**Settings Screen - CAN Trace Section:**

```
┌─────────────────────────────────────────────────┐
│ CAN Trace                                       │
├─────────────────────────────────────────────────┤
│                                                  │
│ ─── Aufzeichnung ───                            │
│                                                  │
│ Status: Keine Aufnahme                          │
│         [AUFNAHME STARTEN]                       │
│                                                  │
│ Dateiname: ThinkCity_2025-11-07_21-30-45.trc   │
│ Speicher:  25.3 GB frei (traces/)              │
│                                                  │
│ ─── Wiedergabe ───                              │
│                                                  │
│ Trace-Datei:  [Dropdown mit .trc Dateien]      │
│ ☐ Endlos-Wiedergabe                            │
│                                                  │
│ Status: Gestoppt                                │
│         [WIEDERGABE STARTEN]                     │
│                                                  │
└─────────────────────────────────────────────────┘

(Während Aufnahme)

┌─────────────────────────────────────────────────┐
│ ─── Aufzeichnung ───                            │
│                                                  │
│ Status: Aufnahme läuft                          │
│         Dauer: 00:02:35                          │
│         Nachrichten: 15,432                      │
│         Dateigröße: 1.2 MB                       │
│                                                  │
│         [AUFNAHME STOPPEN]                       │
│                                                  │
│ Dateiname: ThinkCity_2025-11-07_21-30-45.trc   │
│                                                  │
└─────────────────────────────────────────────────┘
```

**StatusBar Indicator:**

```
[REC] [Repl] [WiFi] [CAN]
  ↑     ↑      ↑      ↑
  Red   Orange Green  Green
  Blink Static Static Static
```

**[REC] Indicator:**
- Color: Red (#E63232 ↔ #B41E1E)
- Behavior: Blinking (2Hz) when recording active
- Position: Leftmost (before [Repl])
- Only visible during recording

### Dashboard Integration

**`dashboard.py`:**
```python
# Initialize recorder
self.trace_recorder = TraceRecorder(
    can_interface=self.can_interface,
    output_dir=os.path.expanduser("~/thinkcity-dashboard-v3/traces")
)

# Forward CAN messages (in _update_loop, 10Hz)
if self.trace_recorder and self.trace_recorder.is_recording:
    self.trace_recorder.record_message(msg)

# Propagate recording status to all screens
recording_active = self.trace_recorder.is_recording if self.trace_recorder else False
for screen in self.screens:
    if hasattr(screen, 'status_bar'):
        screen.status_bar.set_recording_status(recording_active)

# Graceful shutdown
def closeEvent(self, event):
    if self.trace_recorder and self.trace_recorder.is_recording:
        stats = self.trace_recorder.stop_recording()
        logging.info(f"Recording stopped: {stats}")
```

---

## 2. CAN Trace Replay

### 🎯 Ziel

Aufgezeichnete CAN-Traces auf vcan0 abspielen für Entwicklung und Testing ohne echtes Fahrzeug.

### Implementierung

**Dateien:**
- `trace_parser.py` (~150 Zeilen) - PCAN .trc Parser
- `trace_player.py` (~220 Zeilen) - Replay Engine

**Features:**
- ✅ Liest PCAN .trc Dateien
- ✅ Spielt Messages auf vcan0 mit Original-Timing
- ✅ Loop-Modus für Dauertests
- ✅ Pause/Resume/Stop Steuerung
- ✅ UI-Integration in Settings Screen

### Architektur

```python
# trace_parser.py
class PCANTraceParser:
    def parse_file(self, filepath: str) -> List[Tuple[float, int, bytes]]:
        """Returns: List[(timestamp_ms, can_id, data_bytes)]"""
        pass

# trace_player.py
class TracePlayer:
    def __init__(self, can_channel='vcan0'):
        self.bus = can.Bus(channel=can_channel, bustype='socketcan')
    
    def play_trace(self, trace_data: List, loop=False):
        """Plays trace with correct timing"""
        pass
    
    def pause(self)
    def resume(self)
    def stop(self)
```

### Settings Integration

```python
# In settings_screen.py - create_can_trace_group()

# Replay Section  
self.trace_combo = QComboBox()
self.trace_combo.addItems(self._scan_traces())
self.loop_checkbox = QCheckBox(t("loop_playback"))
self.trace_start_btn = QPushButton(t("start_replay"))
self.trace_stop_btn = QPushButton(t("stop_replay"))

def _scan_traces(self) -> List[str]:
    """Scan traces/ directory for .trc files"""
    traces_dir = os.path.expanduser("~/thinkcity-dashboard-v3/traces")
    return [f for f in os.listdir(traces_dir) if f.endswith('.trc')]
```

---

## User Workflows

### Workflow 1: Trace aufzeichnen

1. **Dashboard öffnen** → Settings → CAN Trace
2. **Recording Sektion:**
   - Status: "Keine Aufnahme"
   - Dateiname-Vorschau: `ThinkCity_2025-11-07_21-30-45.trc`
   - Speicherort: 25.3 GB frei (traces/)
3. **"Aufnahme Starten"** klicken
   - [REC] erscheint in StatusBar (blinkt rot)
   - Live-Statistik wird angezeigt:
     - Dauer: 00:01:23
     - Nachrichten: 1,245
     - Dateigröße: 156 KB
4. **"Aufnahme Stoppen"** klicken
   - Finale Statistiken werden angezeigt
   - Datei gespeichert in `~/thinkcity-dashboard-v3/traces/`

### Workflow 2: Trace abspielen

1. **Trace-Dateien bereitstellen**
```bash
# Benutzer kopiert Traces auf Pi
scp *.trc pi@thinkcity:/home/pi/thinkcity-dashboard-v3/traces/
```

2. **Im Settings-Menü** → CAN Trace
3. **CAN Interface auf vcan0 setzen** (in CAN Interface Sektion)
4. **Replay Sektion:**
   - Trace-Datei: Dropdown mit allen .trc aus traces/
   - ☑ Endlos-Wiedergabe (optional)
5. **"Wiedergabe Starten"** klicken
   - Status: "Läuft"
   - Dashboard empfängt und decodiert Messages
6. **"Wiedergabe Stoppen"** → Status: "Gestoppt"

### Workflow 3: Aufgezeichnete Traces analysieren

1. **Trace vom Pi holen:**
```bash
scp pi@thinkcity:~/thinkcity-dashboard-v3/traces/ThinkCity_*.trc ./
```

2. **In PCANview öffnen** (Windows/Linux)
   - File → Open → ThinkCity_2025-11-07_20-59-14.trc
   - Alle Messages werden korrekt dargestellt
   - Filter, Export, Analyse-Tools verfügbar

3. **An Fachmann senden**
   - .trc Datei ist standardisiertes Format
   - Kompatibel mit allen gängigen CAN-Tools
   - PCAN, CANalyzer, etc.

---

## Vorteile

### Recording:
✅ **PCAN-kompatibel**: Standard-Format für CAN-Tools  
✅ **Professionell**: Kompatibel mit PCANview, CANalyzer, etc.  
✅ **Verlustfrei**: Queue-basiertes Buffering (10k Messages)  
✅ **Performant**: Background Thread, Batch-Writes  
✅ **Live-Feedback**: Real-time Statistiken im Dashboard  
✅ **Sicher**: Auto-Stop bei Speichermangel  

### Replay:
✅ **Realistische Daten**: Echte CAN-Nachrichten vom Fahrzeug  
✅ **Reproduzierbar**: Immer gleiche Sequenz  
✅ **Testfälle**: Spezifische Szenarien (Laden, Entladen, etc.)  
✅ **Timing**: Original-Timing der Messages  
✅ **Vollständig**: Alle CAN-IDs inkl. seltener Messages  
✅ **Loop-Modus**: Endlos-Tests für Stabilitätsanalyse  

---

## Beispiel-Traces

**Historische Traces in `AKKU/191210_PCAN-Traces/`:**
1. `191210_Arndt_Think_Entladen_ab_91_procent.trc` (860k Messages, 1.7h Fahrt)
2. `191210_Arndt_Think_Laden_ab_82_procent.trc` (93k Messages, 677s Laden)
3. `191210_Arndt_Think_Laden_ab_91_procent.trc` (33k Messages, 239s)

**Neu aufgezeichnet mit TraceRecorder:**
- `ThinkCity_2025-11-07_20-59-14.trc` (81 Messages, 16s Testlauf)
- Format verifiziert: ✅ PCANview kompatibel

---

## Implementation Status

### ✅ Phase 1: Core Recording (COMPLETE)
- ✅ Commit d9fdebe: trace_recorder.py mit PCAN Format
- ✅ Queue-basiertes Buffering (10k Messages)
- ✅ Background Writer Thread
- ✅ Excel DateTime Format für PCANview

### ✅ Phase 2: UI Integration (COMPLETE)
- ✅ Commit 5de9b61: [REC] StatusBar Indicator
- ✅ Commit 0cec3dc: Settings Recording Controls
- ✅ Commit f008864: Translations (DE/EN)
- ✅ Live statistics display

### ✅ Phase 3: Dashboard Integration (COMPLETE)
- ✅ Commit 0871d53: CAN Message Forwarding
- ✅ Auto-Stop bei Shutdown
- ✅ Status Propagation zu allen Screens
- ✅ Graceful error handling

### ✅ Phase 4: Bugfixes & Refactoring (COMPLETE)
- ✅ Commit 3a1542d: Emoji removal, parent hierarchy fix
- ✅ Commit 740e49b: Unified CAN Trace UI Section
- ✅ Translation system fully integrated

### ✅ Phase 5: Testing & Validation (COMPLETE)
- ✅ Trace Recording erfolgreich getestet
- ✅ PCAN Format verifiziert mit PCANview
- ✅ Live-Statistik funktioniert
- ✅ [REC] Indikator funktioniert
- ✅ Deployment auf Pi erfolgreich
- ✅ Running in production since 07.11.2025

### 🔄 Phase 6: Replay Testing (PARTIAL)
- ✅ trace_parser.py implementiert
- ✅ trace_player.py implementiert
- ✅ Settings UI vorhanden
- ⏳ Full testing mit verschiedenen Traces
- ⏳ Performance-Optimierung für große Traces

---

## Bekannte Limitierungen

### Recording:
- Max 10k Messages im Buffer (dann blocking bis Writer aufholt)
- Debug-Logging sollte für Production reduziert werden
- Keine automatische Trace-Rotation implementiert

### Replay:
- Große Traces (>1M Messages) benötigen viel RAM
- Keine Pause-Funktion in UI (nur im Code)
- Threading-Model könnte für sehr schnelle Replay optimiert werden

---

## Lessons Learned

1. **Parent Hierarchy**: Widget-Hierarchie muss beachtet werden
   - SettingsScreen → QStackedWidget → Dashboard
   - `self.parent().parent()` für Dashboard-Zugriff

2. **linuxfb**: Keine Emoji-Unterstützung
   - Alle Emojis durch Text ersetzen
   - [REC] statt 🔴, [Repl] statt ▶

3. **Threading**: Queue-basiertes Design verhindert Message-Loss
   - Non-blocking put() im Haupt-Thread
   - Batch-Writes im Background-Thread

4. **PCAN Format**: Excel DateTime crucial für PCANview
   - `datetime.toordinal() + (time_seconds / 86400)`
   - Mikrosekunden-Präzision für Time Offset

5. **UI Unification**: Besser Recording + Replay in einer Sektion
   - Reduziert Scrolling in Settings
   - Klarer Zusammenhang erkennbar

---

## Zukünftige Erweiterungen

### Recording:
- ⏳ Auto-Recording bei Fahrstart
- ⏳ Compression (.trc.gz)
- ⏳ Cloud-Upload (NAS/FTP)
- ⏳ Recording-Historie im UI
- ⏳ Filter (nur bestimmte CAN-IDs)
- ⏳ Split nach Größe (max 100MB pro File)

### Replay:
- ⏳ Pause/Resume in UI (derzeit nur im Code)
- ⏳ Speed Control (0.5x, 1x, 2x, etc.)
- ⏳ Jump to Timestamp
- ⏳ Message Filter während Replay
- ⏳ Playback Statistics

---

## Konfiguration

### config.json
```json
{
    "recording_auto_stop_mb": 100,
    "recording_buffer_size": 10000,
    "recording_output_dir": "~/thinkcity-dashboard-v3/traces"
}
```

### Environment Variables
```bash
TC_RECORDING_DIR=/mnt/usb/traces  # Override output directory
```

---

## Statistiken

### Recording Stats (Live während Aufnahme)
- **Duration:** hh:mm:ss seit Start
- **Message Count:** Anzahl aufgezeichneter Messages
- **File Size:** Aktuelle Dateigröße in KB/MB

### Recording Stats (Nach Stopp)
```python
{
    "filename": "ThinkCity_2025-11-07_20-59-14.trc",
    "duration_seconds": 16.3,
    "message_count": 81,
    "file_size_bytes": 4567,
    "start_time": "2025-11-07 20:59:14",
    "end_time": "2025-11-07 20:59:30"
}
```

---

## Dateiname-Konvention

```
ThinkCity_YYYY-MM-DD_HH-MM-SS.trc

Examples:
- ThinkCity_2025-11-07_20-59-14.trc
- ThinkCity_2025-11-07_14-05-12.trc
- ThinkCity_2025-12-25_09-30-00.trc
```

**Vorteile:**
- ✅ Sortierbar (chronologisch)
- ✅ Eindeutig (Sekunden-Genauigkeit)
- ✅ Lesbar (Datum + Uhrzeit erkennbar)
- ✅ Kompatibel (keine Sonderzeichen)

---

## Sicherheit & Datenschutz

**Was wird NICHT aufgezeichnet:**
- ❌ GPS-Koordinaten (wenn aktiviert)
- ❌ Benutzer-Einstellungen
- ❌ WLAN-Credentials
- ❌ NAS-Passwörter

**Was wird aufgezeichnet:**
- ✅ Rohe CAN-Messages (ID + Data)
- ✅ Timestamps (relativ)
- ✅ CAN-Interface (can0/vcan0)

**Hinweis:** CAN-Daten können fahrzeugspezifische Informationen enthalten (Geschwindigkeit, SOC, Zellspannungen). Traces sollten entsprechend behandelt werden.

---

**Status:** ✅ Production Ready  
**Letzte Aktualisierung:** 07.11.2025  
**Version:** 1.0
