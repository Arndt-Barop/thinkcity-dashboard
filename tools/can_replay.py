#!/usr/bin/env python3
"""
CAN trace replay tool
Reads candump log format and replays on CAN interface
"""

import sys
import time
import re
from pathlib import Path
import can


def replay_can_log(log_file, interface='can0', speed_factor=1.0, loop=False):
    """
    Replay CAN log file to interface.
    
    Args:
        log_file: Path to candump log file
        interface: CAN interface name (default: can0)
        speed_factor: Playback speed multiplier (1.0 = realtime, 10.0 = 10x faster)
        loop: Loop playback forever
    """
    print(f"Replaying {log_file} on {interface} (speed: {speed_factor}x)")
    
    # Open CAN bus
    bus = can.interface.Bus(channel=interface, bustype='socketcan')
    
    while True:
        with open(log_file, 'r') as f:
            last_timestamp = 0.0
            frame_count = 0
            
            for line in f:
                # Parse: (timestamp) can0 ID#DATA
                match = re.match(r'\(([\d.]+)\)\s+\w+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)', line)
                if not match:
                    continue
                
                timestamp = float(match.group(1))
                can_id = int(match.group(2), 16)
                data_str = match.group(3)
                
                # Convert hex string to bytes
                data = bytes.fromhex(data_str) if data_str else b''
                
                # Calculate delay
                if frame_count > 0:
                    delay = (timestamp - last_timestamp) / speed_factor
                    if delay > 0:
                        time.sleep(delay)
                
                # Send frame using python-can
                msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
                try:
                    bus.send(msg)
                    frame_count += 1
                    
                    if frame_count % 1000 == 0:
                        print(f"\rReplayed {frame_count} frames ({timestamp:.1f}s)...", end='', flush=True)
                    
                except can.CanError as e:
                    print(f"\nError sending frame {can_id:03X}#{data_str}: {e}")
                    continue
                
                last_timestamp = timestamp
        
        print(f"\n✓ Replay complete: {frame_count} frames, {last_timestamp:.1f} seconds")
        
        if not loop:
            break
        
        print("Looping...")
        time.sleep(1)
    
    bus.shutdown()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: can_replay.py <logfile.log> [interface] [speed_factor] [--loop]")
        print("\nExamples:")
        print("  can_replay.py trace.log                    # Replay at realtime on can0")
        print("  can_replay.py trace.log can0 10.0          # Replay 10x faster")
        print("  can_replay.py trace.log can0 1.0 --loop    # Loop forever")
        sys.exit(1)
    
    log_file = sys.argv[1]
    interface = sys.argv[2] if len(sys.argv) > 2 else 'can0'
    speed_factor = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    loop = '--loop' in sys.argv
    
    if not Path(log_file).exists():
        print(f"Error: File not found: {log_file}")
        sys.exit(1)
    
    try:
        replay_can_log(log_file, interface, speed_factor, loop)
    except KeyboardInterrupt:
        print("\n\nReplay stopped by user")
