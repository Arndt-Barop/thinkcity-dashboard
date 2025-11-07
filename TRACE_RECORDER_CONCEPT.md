# 🎥 Trace Recorder Feature - Konzept & Implementierung

## Übersicht

**Ziel:** CAN-Bus Traffic in Echtzeit aufzeichnen und als PCAN .trc Datei speichern, kompatibel mit PCANview und anderen Analysetools.

**Use Cases:**
- 📊 Fahrdaten für spätere Analyse aufzeichnen
- 🐛 Fehlerdiagnose mit Fachmann-Support
- 🔬 Unbekannte CAN-IDs erforschen
- 📈 Performance-Analyse über längere Zeiträume
- 🎓 Lernmaterial für CAN-Bus Entwicklung

---

## 📋 Anforderungen

### Funktional
- ✅ Aufzeichnung von CAN-Messages in PCAN .trc Format
- ✅ Start/Stop/Pause Funktionalität
- ✅ Automatische Dateinamen mit Timestamp (ThinkCity_2025-11-07_20-15-30.trc)
- ✅ Metadaten (FILEVERSION, STARTTIME, Start datetime)
- ✅ Kompatibilität mit can0 und vcan0
- ✅ [REC] Status-Indikator in StatusBar (rot blinkend während Aufnahme)
- ✅ Aufnahme-Statistik (Dauer, Message-Count, Dateigröße)
- ✅ Speicherverwaltung (Auto-Stop bei <100MB freiem Speicher)

### Nicht-Funktional
- ⚡ Performance: Kein Einfluss auf Dashboard-Performance
- 💾 Speicher: Traces in ~/thinkcity-dashboard-v3/traces/ (mit anderen Traces)
- 🔒 Sicherheit: Keine Aufzeichnung von sensiblen Daten (nur CAN raw data)
- 🎯 Genauigkeit: Timestamps mit Millisekunden-Präzision

---

## 🏗️ Architektur

### Neue Komponenten

#### 1. **trace_recorder.py**
```python
class TraceRecorder:
    """
    Records CAN messages to PCAN .trc format.
    Thread-safe, non-blocking.
    """
    
    def __init__(self, can_interface: str, output_dir: str)
    def start_recording(self, filename: Optional[str] = None) -> bool
    def stop_recording(self) -> dict  # Returns stats
    def pause_recording(self)
    def resume_recording(self)
    def is_recording(self) -> bool
    def get_stats(self) -> dict  # Duration, message count, file size
    def _record_message(self, msg)  # Internal callback
    def _write_header(self)
    def _write_message(self, timestamp, can_id, data)
```

**Format-Spezifikation:**
```
;$FILEVERSION=1.1
;$STARTTIME=43809.2974678819
;   Start time: 07.11.2025 20:15:30.125.0
;---+--   ----+----  --+--  ----+---  +  -+ -- -- -- -- -- -- --
     1)         0.0  Rx         0251  8  40 00 00 00 00 00 00 00
     2)        10.5  Rx         0301  8  12 34 56 78 9A BC DE F0
```

#### 2. **widgets.py - StatusBar Erweiterung**
```python
class StatusBar:
    recording_active: bool = False  # New flag
    
    def set_recording_status(self, active: bool):
        """Update [REC] indicator"""
        
    def paintEvent(self, event):
        # Add [REC] indicator (red, blinking)
        # Position: after [Repl], before [WiFi]
        # Example: [REC] [Repl] [WiFi]
```

#### 3. **settings_screen.py - Recording Controls**
```python
def create_trace_recording_group(self):
    """
    Recording Controls Group
    - Status: Not Recording / Recording (Duration, Messages, Size)
    - Start Button (green)
    - Stop Button (red)
    - Filename preview
    - Storage info (free space)
    """
```

#### 4. **dashboard.py - Integration**
```python
# Initialize recorder
self.trace_recorder = TraceRecorder(
    can_interface=self.config['can_interface'],
    output_dir=os.path.expanduser("~/thinkcity-dashboard-v3/traces")
)

# Update loop: propagate recording status
if hasattr(self, 'trace_recorder'):
    recording_active = self.trace_recorder.is_recording()
    for screen in self.screens:
        screen.status_bar.set_recording_status(recording_active)
```

---

## 📊 Dateiformat Details

### Header
```
;$FILEVERSION=1.1
;$STARTTIME=45257.8437500000
;   Start time: 07.11.2025 20:15:30.125.0
;
;   Message   Time    Type ID     DLC Data Bytes
;   Number    Offset  
;---+--   ----+----  --+--  ----+---  +  -+ -- -- -- -- -- -- --
```

### Message Lines
```
     1)         0.0  Rx         0251  8  40 00 00 00 00 00 00 00
     ↑          ↑    ↑          ↑     ↑  ↑
     Number     ms   Rx/Tx      ID   DLC Data
```

**Formatting Rules:**
- Message Number: Right-aligned, 6 characters
- Timestamp: Relative to start time in milliseconds, 1 decimal place
- Direction: Always "Rx" for received messages
- CAN-ID: 4 hex digits (e.g., 0251, 0301)
- DLC: 1 digit (0-8)
- Data: Space-separated hex bytes (uppercase)

---

## 🎨 UI/UX Design

### Settings Screen - Recording Section

```
┌─────────────────────────────────────────────────┐
│ 🎥 CAN Trace Recording                          │
├─────────────────────────────────────────────────┤
│                                                  │
│ Status: ⭕ Not Recording                         │
│         [START RECORDING]                        │
│                                                  │
│ Filename: ThinkCity_2025-11-07_20-15-30.trc    │
│ Storage:  2.3 GB free (traces/)                 │
│                                                  │
└─────────────────────────────────────────────────┘

(After starting)

┌─────────────────────────────────────────────────┐
│ 🎥 CAN Trace Recording                          │
├─────────────────────────────────────────────────┤
│                                                  │
│ Status: 🔴 RECORDING                            │
│         Duration: 00:02:35                       │
│         Messages: 15,432                         │
│         File Size: 1.2 MB                        │
│                                                  │
│         [⏸ PAUSE]    [⏹ STOP]                   │
│                                                  │
│ Filename: ThinkCity_2025-11-07_20-15-30.trc    │
│ Storage:  2.3 GB free (traces/)                 │
│                                                  │
└─────────────────────────────────────────────────┘
```

### StatusBar Indicator

```
[REC] [Repl] [WiFi]
  ↑     ↑      ↑
  Red   Orange Green
  Blink Normal Normal
```

**[REC] Indicator:**
- Color: Red (#e74c3c)
- Behavior: Blinking (0.5s on/off) when recording
- Position: Leftmost (before [Repl])
- Only shown when recording active

---

## ⚙️ Technische Implementierung

### Threading Model
```
Main Thread (Dashboard)
    ↓
CAN Reader Thread (can_interface)
    ↓
TraceRecorder (non-blocking)
    → Message Queue
    → Writer Thread (background)
        → Flush to file every 100 messages
```

### Message Flow
1. CAN message arrives in `can_interface`
2. Dashboard calls `can_decoder.parse(msg)`
3. **NEW:** If recorder active: `trace_recorder.record_message(msg)`
4. Recorder adds message to queue
5. Writer thread flushes queue to file

### Performance Considerations
- **Buffer Size:** 1000 messages before flush
- **Write Frequency:** Max every 100ms
- **Memory Limit:** Max 10MB queue (auto-stop if exceeded)
- **CPU Impact:** <2% additional load

### Storage Management
```python
def check_storage_space(self) -> float:
    """Returns free space in GB"""
    st = os.statvfs(self.output_dir)
    free_bytes = st.f_bavail * st.f_frsize
    return free_bytes / (1024**3)

def should_stop_recording(self) -> bool:
    """Auto-stop if < 100MB free"""
    return self.check_storage_space() < 0.1
```

---

## 🔧 Konfiguration

### Settings in config.json
```json
{
    "recording_auto_stop_mb": 100,
    "recording_buffer_size": 1000,
    "recording_output_dir": "~/thinkcity-dashboard-v3/traces"
}
```

### Environment Variables
```bash
TC_RECORDING_DIR=/mnt/usb/traces  # Override output directory
```

---

## 📈 Statistiken

### Real-time Stats (während Aufnahme)
- **Duration:** hh:mm:ss seit Start
- **Message Count:** Anzahl aufgezeichneter Messages
- **Message Rate:** Messages/Sekunde
- **File Size:** Aktuelle Dateigröße in MB
- **Unique CAN-IDs:** Anzahl verschiedener IDs

### Post-Recording Stats
```python
{
    "filename": "ThinkCity_2025-11-07_20-15-30.trc",
    "duration_seconds": 155.3,
    "message_count": 15432,
    "file_size_mb": 1.2,
    "unique_can_ids": 23,
    "average_rate_hz": 99.4,
    "start_time": "2025-11-07 20:15:30",
    "end_time": "2025-11-07 20:18:05"
}
```

---

## ✅ Implementierungs-Checklist

### Phase 1: Core Recorder (CURRENT)
- [ ] TraceRecorder Klasse erstellen
- [ ] PCAN Format Writer implementieren
- [ ] Threading Model (Message Queue + Writer Thread)
- [ ] Unit Tests für Format-Konformität

### Phase 2: UI Integration
- [ ] StatusBar [REC] Indikator (mit Blink-Animation)
- [ ] Settings Screen Recording Section
- [ ] Start/Stop/Pause Buttons
- [ ] Real-time Statistik-Anzeige

### Phase 3: Dashboard Integration
- [ ] TraceRecorder in dashboard.py integrieren
- [ ] Message Flow: can_interface → recorder
- [ ] Status-Updates an alle StatusBars propagieren
- [ ] Speicherverwaltung (Auto-Stop)

### Phase 4: Testing & Polish
- [ ] Test mit echtem CAN-Bus (can0)
- [ ] Test mit vcan0 + Trace Replay
- [ ] PCANview Kompatibilitätstest
- [ ] Performance-Test (1000+ msg/s)
- [ ] Dokumentation aktualisieren

---

## 🚀 Erweiterte Features (Future)

### Phase 5: Advanced Features (Optional)
- ⏳ Auto-Recording bei Fahrstart
- ⏳ Compression (.trc.gz)
- ⏳ Cloud-Upload (NAS/FTP)
- ⏳ Recording-Historie (letzten 10 Recordings)
- ⏳ Filter (nur bestimmte CAN-IDs)
- ⏳ Split nach Größe (max 100MB pro File)
- ⏳ Annotations (Marker für Events)

---

## 📝 Dateinamen-Konvention

```
ThinkCity_YYYY-MM-DD_HH-MM-SS.trc

Examples:
- ThinkCity_2025-11-07_20-15-30.trc
- ThinkCity_2025-11-07_14-05-12.trc
- ThinkCity_2025-12-25_09-30-00.trc
```

**Vorteile:**
- ✅ Sortierbar (chronologisch)
- ✅ Eindeutig (Sekunden-Genauigkeit)
- ✅ Lesbar (Datum + Uhrzeit erkennbar)
- ✅ Kompatibel (keine Sonderzeichen)

---

## 🔒 Sicherheit & Datenschutz

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

## 📚 Verwendung

### Workflow
1. **Vorbereitung:** Settings öffnen → Trace Recording Sektion
2. **Start:** "Start Recording" Button → [REC] erscheint in StatusBar
3. **Fahrt:** Dashboard nutzen wie gewohnt (kein Performance-Einfluss)
4. **Stop:** "Stop Recording" Button → Statistik wird angezeigt
5. **Datei:** Trace-Datei in `traces/` Verzeichnis verfügbar
6. **Analyse:** Mit PCANview öffnen oder per NAS/USB exportieren

### Mit PCANview öffnen
```bash
# Datei vom Pi kopieren
scp pi@10.42.0.214:~/thinkcity-dashboard-v3/traces/ThinkCity_*.trc .

# In PCANview öffnen
# File → Open Trace File → ThinkCity_2025-11-07_20-15-30.trc
```

---

## 🎯 Erfolgs-Kriterien

✅ **Funktionalität:**
- Aufzeichnung läuft stabil über 30+ Minuten
- Alle CAN-Messages werden korrekt erfasst
- Datei ist mit PCANview lesbar

✅ **Performance:**
- <2% CPU-Last zusätzlich
- <10MB RAM zusätzlich
- Keine Dashboard-Verzögerungen

✅ **Usability:**
- Start/Stop in <2 Sekunden
- [REC] Indikator gut sichtbar
- Statistiken in Echtzeit

---

## 📅 Zeitplan

- **Phase 1 (Core):** 2 Stunden → TraceRecorder Klasse
- **Phase 2 (UI):** 1 Stunde → StatusBar + Settings
- **Phase 3 (Integration):** 1 Stunde → Dashboard + Testing
- **Phase 4 (Testing):** 1 Stunde → Validation + Bugfixes

**Total:** ~5 Stunden

---

**Status:** 🚧 In Entwicklung (Phase 1 - Core Recorder)
**Letzte Aktualisierung:** 07.11.2025
**Version:** 1.0
