#!/usr/bin/env python3
"""
PCAN TRC to candump log converter
Converts PCAN-View .trc files to candump format for replay with canplayer
"""

import sys
import re
from pathlib import Path


def parse_trc_line(line):
    """Parse a single TRC data line."""
    # Example: "     1)         2.1  Rx         0251  8  40 00 00 00 00 00 00 00"
    line = line.strip()
    if not line or line.startswith(';') or line.startswith('-'):
        return None
    
    # Match the TRC format
    match = re.match(r'\s*\d+\)\s+([\d.]+)\s+\w+\s+([0-9A-Fa-f]+)\s+(\d+)\s+(.*)', line)
    if not match:
        return None
    
    timestamp_ms = float(match.group(1))
    can_id = match.group(2)
    dlc = int(match.group(3))
    data_str = match.group(4).strip()
    
    # Parse data bytes
    data_bytes = []
    if data_str:
        data_bytes = [b.strip() for b in data_str.split() if b.strip()]
    
    return {
        'timestamp': timestamp_ms / 1000.0,  # Convert to seconds
        'id': can_id,
        'dlc': dlc,
        'data': data_bytes[:dlc]  # Only take DLC bytes
    }


def trc_to_candump(trc_file, output_file=None):
    """Convert TRC file to candump format."""
    if output_file is None:
        output_file = Path(trc_file).with_suffix('.log')
    
    print(f"Converting {trc_file} -> {output_file}")
    
    frames_written = 0
    start_time = None
    
    with open(trc_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w') as outfile:
            for line_num, line in enumerate(infile, 1):
                parsed = parse_trc_line(line)
                if parsed is None:
                    continue
                
                # Set start time from first frame
                if start_time is None:
                    start_time = parsed['timestamp']
                
                # Calculate relative timestamp
                rel_time = parsed['timestamp'] - start_time
                
                # Format: (timestamp) can0 ID#DATA
                # Example: (0.000000) can0 251#4000000000000000
                # Ensure ID is zero-padded to 3 hex digits for standard 11-bit IDs
                can_id_formatted = parsed['id'].upper().zfill(3)
                data_hex = ''.join(parsed['data'])
                candump_line = f"({rel_time:.6f}) can0 {can_id_formatted}#{data_hex}\n"
                outfile.write(candump_line)
                frames_written += 1
    
    print(f"✓ Converted {frames_written} CAN frames")
    print(f"✓ Duration: {rel_time:.1f} seconds ({rel_time/60:.1f} minutes)")
    return output_file


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: trc2candump.py <input.trc> [output.log]")
        print("\nConverts PCAN TRC files to candump format for replay")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    result = trc_to_candump(input_file, output_file)
    print(f"\nReady to replay with:")
    print(f"  canplayer -I {result} -l i")
