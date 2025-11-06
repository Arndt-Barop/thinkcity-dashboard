# trace_parser.py
# Parser for PCAN-View .trc Trace-Dateien

import os
import re
from typing import List, Tuple, Optional

class PCANTraceParser:
    """
    Parser für PCAN-View Trace-Dateien (.trc Format).
    
    Format:
        ;$FILEVERSION=1.1
        ;$STARTTIME=43809.2974678819
        ;   Start time: 10.12.2019 07:08:21.225.0
        ;---+--   ----+----  --+--  ----+---  +  -+ -- -- -- -- -- -- --
             1)         2.1  Rx         0251  8  40 00 00 00 00 00 00 00 
             2)        11.4  Rx         0460  8  03 E0 00 00 00 00 00 00 
    
    Data lines: Number) Time_ms Rx/Tx CAN-ID Länge Daten...
    """
    
    def __init__(self, filepath: str):
        """
        Args:
            filepath: Pfad zur .trc Datei
        """
        self.filepath = filepath
        self.metadata = {}
        self.messages = []
    
    def parse(self) -> List[Tuple[float, int, bytes]]:
        """
        Parse the trace-Datei and returns CAN-Messages back.
        
        Returns:
            List of tuples: (timestamp_ms, can_id, data_bytes)
        
        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Bei ungültigem Format
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Trace file not found: {self.filepath}")
        
        self.messages = []
        
        with open(self.filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments und leere Zeilen
                if not line or line.startswith(';'):
                    self._parse_metadata(line)
                    continue
                
                # Parse data line
                try:
                    msg = self._parse_message_line(line)
                    if msg:
                        self.messages.append(msg)
                except Exception as e:
                    print(f"Warning: Could not parse line {line_num}: {line[:50]}... ({e})")
                    continue
        
        print(f"Parsed {len(self.messages)} CAN messages from {os.path.basename(self.filepath)}")
        return self.messages
    
    def _parse_metadata(self, line: str):
        """Extract metadata aus Kommentarzeilen."""
        if line.startswith(';$FILEVERSION='):
            self.metadata['version'] = line.split('=')[1]
        elif line.startswith(';$STARTTIME='):
            self.metadata['starttime'] = line.split('=')[1]
        elif 'Start time:' in line:
            # ;   Start time: 10.12.2019 07:08:21.225.0
            match = re.search(r'Start time:\s+(.+)', line)
            if match:
                self.metadata['start_datetime'] = match.group(1).strip()
    
    def _parse_message_line(self, line: str) -> Optional[Tuple[float, int, bytes]]:
        """
        Parse a single CAN-Message Zeile.
        
        Format: Number) Time_ms Rx/Tx CAN-ID Länge Daten...
        Example: 1) 2.1 Rx 0251 8 40 00 00 00 00 00 00 00
        
        Returns:
            Tuple (timestamp_ms, can_id, data_bytes) oder None
        """
        # Regex: Number) Time Rx/Tx CAN-ID Length Data
        # Flexible for different spacing variants
        pattern = r'^\s*\d+\)\s+([\d.]+)\s+(?:Rx|Tx)\s+([0-9A-Fa-f]+)\s+(\d+)\s+(.*)$'
        match = re.match(pattern, line)
        
        if not match:
            return None
        
        timestamp_ms = float(match.group(1))
        can_id_hex = match.group(2)
        dlc = int(match.group(3))
        data_str = match.group(4).strip()
        
        # Parse CAN-ID (hex)
        can_id = int(can_id_hex, 16)
        
        # Parse Data Bytes
        if data_str:
            data_bytes = bytes.fromhex(data_str.replace(' ', ''))
        else:
            data_bytes = b''
        
        # Validierung
        if len(data_bytes) != dlc:
            print(f"Warning: DLC mismatch - expected {dlc}, got {len(data_bytes)} bytes")
        
        return (timestamp_ms, can_id, data_bytes)
    
    def get_metadata(self) -> dict:
        """Gibt Trace-Metadaten back."""
        return self.metadata
    
    def get_duration_seconds(self) -> float:
        """Calculate total duration des Traces in Sekunden."""
        if not self.messages:
            return 0.0
        
        first_ts = self.messages[0][0]
        last_ts = self.messages[-1][0]
        return (last_ts - first_ts) / 1000.0
    
    def get_message_count(self) -> int:
        """Returns number der Messages back."""
        return len(self.messages)
    
    def get_unique_can_ids(self) -> set:
        """Returns all occurring CAN-IDs back."""
        return set(msg[1] for msg in self.messages)


def main():
    """Test-Funktion für Parser."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 trace_parser.py <trace_file.trc>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    print(f"Parsing {filepath}...")
    parser = PCANTraceParser(filepath)
    messages = parser.parse()
    
    print(f"\n=== Trace Info ===")
    print(f"File: {os.path.basename(filepath)}")
    print(f"Messages: {parser.get_message_count()}")
    print(f"Duration: {parser.get_duration_seconds():.1f} seconds")
    print(f"Unique CAN IDs: {len(parser.get_unique_can_ids())}")
    
    metadata = parser.get_metadata()
    if metadata:
        print(f"\n=== Metadata ===")
        for key, value in metadata.items():
            print(f"{key}: {value}")
    
    print(f"\n=== CAN IDs ===")
    can_ids = sorted(parser.get_unique_can_ids())
    for i in range(0, len(can_ids), 8):
        chunk = can_ids[i:i+8]
        print("  " + "  ".join(f"0x{cid:03X}" for cid in chunk))
    
    print(f"\n=== First 10 Messages ===")
    for i, (ts, can_id, data) in enumerate(messages[:10]):
        data_hex = ' '.join(f'{b:02X}' for b in data)
        print(f"{i+1:3d}) {ts:8.1f}ms  0x{can_id:03X}  [{len(data)}]  {data_hex}")
    
    print("\n✓ Parser test completed")


if __name__ == "__main__":
    main()
