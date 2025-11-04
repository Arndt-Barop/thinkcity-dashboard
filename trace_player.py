# trace_player.py
# PCAN Trace File Player für Testing ohne echten CAN-Bus

import re
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CANMessage:
    """Parsed CAN-Message aus Trace."""
    timestamp_ms: float
    arbid: int
    data: bytes
    
    def __repr__(self):
        data_hex = ' '.join(f'{b:02X}' for b in self.data)
        return f"0x{self.arbid:03X}: {data_hex}"


class TracePlayer:
    """
    Spielt PCAN Trace-Files (.trc) ab.
    Perfekt für Testing ohne echten CAN-Bus!
    """
    
    def __init__(self, trace_file: str, loop: bool = True, speed: float = 1.0):
        """
        Args:
            trace_file: Pfad zur .trc Datei
            loop: Endlos-Wiederholung
            speed: Abspiel-Geschwindigkeit (1.0 = Echtzeit, 2.0 = doppelt so schnell)
        """
        self.trace_file = trace_file
        self.loop = loop
        self.speed = speed
        self.messages: List[CANMessage] = []
        self._load_trace()
    
    def _load_trace(self):
        """Lädt und parst Trace-Datei."""
        print(f"Loading trace: {self.trace_file}")
        
        with open(self.trace_file, 'r') as f:
            for line in f:
                # Parse PCAN Format:
                # 1) 1.1 Rx 0301 8 00 00 0F 34 00 58 00 78
                match = re.match(
                    r'\s+\d+\)\s+([\d.]+)\s+Rx\s+([0-9A-F]{4})\s+\d+\s+((?:[0-9A-F]{2}\s*)+)',
                    line
                )
                
                if match:
                    timestamp_ms = float(match.group(1))
                    arbid = int(match.group(2), 16)
                    data_str = match.group(3).strip()
                    data = bytes.fromhex(data_str.replace(' ', ''))
                    
                    msg = CANMessage(timestamp_ms, arbid, data)
                    self.messages.append(msg)
        
        print(f"  Loaded {len(self.messages)} messages")
        
        if self.messages:
            duration = self.messages[-1].timestamp_ms / 1000.0
            unique_ids = len(set(m.arbid for m in self.messages))
            print(f"  Duration: {duration:.1f}s")
            print(f"  Unique IDs: {unique_ids}")
    
    def play(self, callback):
        """
        Spielt Trace ab und ruft Callback für jede Message.
        
        Args:
            callback: Funktion(arbid: int, data: bytes) -> None
        """
        if not self.messages:
            print("No messages to play!")
            return
        
        print(f"\nPlaying trace at {self.speed}x speed (loop={self.loop})...")
        
        try:
            while True:
                start_time = time.time()
                last_timestamp = 0.0
                
                for msg in self.messages:
                    # Warte bis zum nächsten Message
                    delta_ms = msg.timestamp_ms - last_timestamp
                    sleep_time = (delta_ms / 1000.0) / self.speed
                    
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    # Callback
                    callback(msg.arbid, msg.data)
                    
                    last_timestamp = msg.timestamp_ms
                
                if not self.loop:
                    break
                
                elapsed = time.time() - start_time
                print(f"  Loop complete in {elapsed:.1f}s, restarting...")
        
        except KeyboardInterrupt:
            print("\nStopped by user")
    
    def get_unique_ids(self) -> List[int]:
        """Gibt Liste der eindeutigen CAN-IDs zurück."""
        return sorted(set(m.arbid for m in self.messages))
    
    def get_messages_by_id(self, arbid: int) -> List[CANMessage]:
        """Gibt alle Messages mit bestimmter ID zurück."""
        return [m for m in self.messages if m.arbid == arbid]
    
    def analyze(self):
        """Analysiert Trace und zeigt Statistiken."""
        print(f"\n=== Trace Analysis: {self.trace_file} ===\n")
        
        unique_ids = self.get_unique_ids()
        
        print(f"Total Messages: {len(self.messages)}")
        print(f"Unique IDs: {len(unique_ids)}\n")
        
        print("ID Distribution:")
        print("ID     | Count | Rate (Hz) | Example Data")
        print("-------|-------|-----------|" + "-" * 50)
        
        duration = self.messages[-1].timestamp_ms / 1000.0
        
        for arbid in unique_ids:
            msgs = self.get_messages_by_id(arbid)
            count = len(msgs)
            rate = count / duration if duration > 0 else 0
            
            # Beispiel-Daten (erste Message)
            example = ' '.join(f'{b:02X}' for b in msgs[0].data) if msgs else ''
            
            print(f"0x{arbid:03X} | {count:5d} | {rate:6.1f}    | {example}")


# CLI Tool
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="PCAN Trace Player")
    parser.add_argument("trace_file", help="Path to .trc file")
    parser.add_argument("--analyze", action="store_true", help="Analyze trace and exit")
    parser.add_argument("--loop", action="store_true", help="Loop playback")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed (default: 1.0)")
    parser.add_argument("--filter", help="Filter by ID (hex, e.g. 0x301)")
    
    args = parser.parse_args()
    
    player = TracePlayer(args.trace_file, loop=args.loop, speed=args.speed)
    
    if args.analyze:
        player.analyze()
        sys.exit(0)
    
    # Playback mit Print
    def print_message(arbid: int, data: bytes):
        if args.filter:
            filter_id = int(args.filter, 16)
            if arbid != filter_id:
                return
        
        data_hex = ' '.join(f'{b:02X}' for b in data)
        print(f"  0x{arbid:03X}: {data_hex}")
    
    player.play(print_message)
