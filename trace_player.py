# trace_player.py
# CAN Trace Player für vcan0 mit originalem Timing

import time
import threading
from typing import Optional, List, Tuple
from trace_parser import PCANTraceParser

try:
    import can
    CAN_AVAILABLE = True
except ImportError:
    CAN_AVAILABLE = False
    print("Warning: python-can not installed. Install with: pip3 install python-can")

class TracePlayer:
    """
    Spielt PCAN Trace-Dateien auf einem virtuellen CAN-Bus (vcan0) ab.
    Verwendet das originale Timing aus dem Trace.
    """
    
    def __init__(self, interface: str = 'vcan0', bitrate: int = 500000):
        """
        Args:
            interface: CAN-Interface (z.B. 'vcan0', 'can0')
            bitrate: Bitrate in bps (wird bei vcan ignoriert)
        """
        self.interface = interface
        self.bitrate = bitrate
        self.bus: Optional[can.Bus] = None
        self.messages: List[Tuple[float, int, bytes]] = []
        self.current_trace: Optional[str] = None
        
        # Playback Control
        self.is_playing = False
        self.is_paused = False
        self.loop_enabled = False
        self.playback_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Statistiken
        self.messages_sent = 0
        self.start_time = 0.0
        self.current_position = 0
    
    def load_trace(self, trace_file: str):
        """
        Lädt eine Trace-Datei.
        
        Args:
            trace_file: Pfad zur .trc Datei
        
        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Bei Parsing-Fehler
        """
        print(f"Loading trace: {trace_file}")
        parser = PCANTraceParser(trace_file)
        self.messages = parser.parse()
        self.current_trace = trace_file
        
        metadata = parser.get_metadata()
        duration = parser.get_duration_seconds()
        
        print(f"✓ Loaded {len(self.messages)} messages, duration: {duration:.1f}s")
        if 'start_datetime' in metadata:
            print(f"  Original recording: {metadata['start_datetime']}")
    
    def connect(self):
        """Verbindet zum CAN-Bus."""
        if not CAN_AVAILABLE:
            raise RuntimeError("python-can not installed. Install with: pip3 install python-can")
        
        if self.bus:
            print(f"Already connected to {self.interface}")
            return
        
        try:
            self.bus = can.Bus(interface='socketcan', channel=self.interface, bitrate=self.bitrate)
            print(f"✓ Connected to {self.interface}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {self.interface}: {e}")
    
    def disconnect(self):
        """Trennt die CAN-Bus Verbindung."""
        if self.bus:
            self.bus.shutdown()
            self.bus = None
            print(f"✓ Disconnected from {self.interface}")
    
    def start(self, loop: bool = False):
        """
        Startet das Abspielen des Traces.
        
        Args:
            loop: Wenn True, wird der Trace endlos wiederholt
        """
        if not self.messages:
            raise ValueError("No trace loaded. Call load_trace() first.")
        
        if not self.bus:
            raise ValueError("Not connected. Call connect() first.")
        
        if self.is_playing:
            print("Already playing")
            return
        
        self.loop_enabled = loop
        self.is_playing = True
        self.is_paused = False
        self.stop_event.clear()
        
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()
        
        print(f"▶ Started playback (loop={'ON' if loop else 'OFF'})")
    
    def pause(self):
        """Pausiert das Abspielen."""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            print("⏸ Paused")
    
    def resume(self):
        """Setzt das Abspielen fort."""
        if self.is_playing and self.is_paused:
            self.is_paused = False
            print("▶ Resumed")
    
    def stop(self):
        """Stoppt das Abspielen."""
        if not self.is_playing:
            return
        
        self.stop_event.set()
        self.is_playing = False
        
        if self.playback_thread:
            self.playback_thread.join(timeout=2.0)
        
        print(f"■ Stopped (sent {self.messages_sent} messages)")
    
    def _playback_loop(self):
        """Haupt-Playback-Loop (läuft in separatem Thread)."""
        self.messages_sent = 0
        
        while not self.stop_event.is_set():
            self.current_position = 0
            iteration_start = time.time()
            
            # Sende alle Messages mit originalem Timing
            prev_timestamp = 0.0
            
            for i, (timestamp_ms, can_id, data) in enumerate(self.messages):
                if self.stop_event.is_set():
                    break
                
                # Pause-Handling
                while self.is_paused and not self.stop_event.is_set():
                    time.sleep(0.1)
                
                if self.stop_event.is_set():
                    break
                
                # Berechne Wartezeit bis zur nächsten Message
                delta_ms = timestamp_ms - prev_timestamp
                if delta_ms > 0:
                    time.sleep(delta_ms / 1000.0)
                
                # Sende CAN-Message
                try:
                    msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
                    self.bus.send(msg)
                    self.messages_sent += 1
                    self.current_position = i + 1
                except Exception as e:
                    print(f"Error sending message: {e}")
                
                prev_timestamp = timestamp_ms
            
            # Loop-Handling
            if not self.loop_enabled:
                break
            
            # Kurze Pause zwischen Loop-Iterationen
            if not self.stop_event.is_set():
                time.sleep(0.5)
        
        self.is_playing = False
        print(f"✓ Playback finished ({self.messages_sent} messages sent)")
    
    def get_status(self) -> dict:
        """
        Gibt aktuellen Playback-Status zurück.
        
        Returns:
            Dict mit Status-Informationen
        """
        return {
            'playing': self.is_playing,
            'paused': self.is_paused,
            'loop': self.loop_enabled,
            'trace': self.current_trace,
            'messages_total': len(self.messages),
            'messages_sent': self.messages_sent,
            'position': self.current_position
        }


def main():
    """Test-Funktion für TracePlayer."""
    import sys
    import signal
    
    if len(sys.argv) < 2:
        print("Usage: python3 trace_player.py <trace_file.trc> [--loop]")
        print("\nExample:")
        print("  python3 trace_player.py trace.trc")
        print("  python3 trace_player.py trace.trc --loop")
        sys.exit(1)
    
    trace_file = sys.argv[1]
    loop = '--loop' in sys.argv
    
    # Erstelle und starte Player
    player = TracePlayer(interface='vcan0')
    
    # Signal-Handler für sauberes Beenden
    def signal_handler(sig, frame):
        print("\n\n^C caught, stopping...")
        player.stop()
        player.disconnect()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        player.load_trace(trace_file)
        player.connect()
        player.start(loop=loop)
        
        print("\nPlayback running...")
        print("Press Ctrl+C to stop\n")
        
        # Status-Ausgabe alle 5 Sekunden
        while player.is_playing:
            time.sleep(5.0)
            status = player.get_status()
            print(f"Status: {status['messages_sent']}/{status['messages_total']} messages sent")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        player.stop()
        player.disconnect()


if __name__ == "__main__":
    main()
