#!/usr/bin/env python3
# test_trace_replay.py
# Standalone-Test für Parser und Player (ohne CAN-Bus)

import sys
import os

# Import unserer Module
from trace_parser import PCANTraceParser
from trace_player import TracePlayer

def test_parser(trace_file: str):
    """Test Parser."""
    print("=" * 70)
    print("TEST 1: PCAN Trace Parser")
    print("=" * 70)
    
    parser = PCANTraceParser(trace_file)
    messages = parser.parse()
    
    print(f"\n✓ Parser Test PASSED")
    print(f"  Messages: {len(messages)}")
    print(f"  Duration: {parser.get_duration_seconds():.1f}s")
    print(f"  CAN IDs: {len(parser.get_unique_can_ids())}")
    
    # Zeige erste 5 Messages
    print(f"\nFirst 5 messages:")
    for i, (ts, can_id, data) in enumerate(messages[:5]):
        data_hex = ' '.join(f'{b:02X}' for b in data)
        print(f"  {i+1}) {ts:8.1f}ms  0x{can_id:03X}  [{len(data)}]  {data_hex}")
    
    return True

def test_player_load(trace_file: str):
    """Test Player Loading (ohne CAN-Bus Connection)."""
    print("\n" + "=" * 70)
    print("TEST 2: Trace Player (Load Only)")
    print("=" * 70)
    
    player = TracePlayer(interface='vcan0')
    player.load_trace(trace_file)
    
    status = player.get_status()
    
    print(f"\n✓ Player Load Test PASSED")
    print(f"  Trace: {os.path.basename(status['trace'])}")
    print(f"  Messages: {status['messages_total']}")
    print(f"  Playing: {status['playing']}")
    print(f"  Loop: {status['loop']}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_trace_replay.py <trace_file.trc>")
        print("\nExample:")
        print("  python3 test_trace_replay.py ~/Dokumente/Think/AKKU/191210_PCAN-Traces/191210_Arndt_Think_Laden_ab_91_procent.trc")
        sys.exit(1)
    
    trace_file = sys.argv[1]
    
    if not os.path.exists(trace_file):
        print(f"Error: File not found: {trace_file}")
        sys.exit(1)
    
    print(f"\nTesting with: {os.path.basename(trace_file)}\n")
    
    try:
        # Test 1: Parser
        test_parser(trace_file)
        
        # Test 2: Player Load
        test_player_load(trace_file)
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nNOTE: CAN-Bus playback test skipped (requires vcan0)")
        print("      To test CAN playback:")
        print("        1. sudo modprobe vcan")
        print("        2. sudo ip link add dev vcan0 type vcan")
        print("        3. sudo ip link set up vcan0")
        print("        4. python3 trace_player.py <trace.trc> --loop")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
