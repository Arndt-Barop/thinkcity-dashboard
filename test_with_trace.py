#!/usr/bin/env python3
# test_with_trace.py
# Testet Dashboard mit echten CAN-Traces

import sys
import time
from trace_player import TracePlayer
from can_decoder import CANDecoder

def test_decoder_with_trace(trace_file: str):
    """Testet CAN-Decoder mit Trace-Daten."""
    
    print("=" * 70)
    print("ThinkCity CAN-Decoder Test mit Trace-Daten")
    print("=" * 70)
    
    # Init
    player = TracePlayer(trace_file, loop=False, speed=100.0)  # 100x schneller
    decoder = CANDecoder()
    state = {}
    
    # Statistiken
    stats = {
        "total": 0,
        "decoded": 0,
        "unknown": 0,
        "by_id": {}
    }
    
    def process_message(arbid: int, data: bytes):
        stats["total"] += 1
        
        # Dekodieren
        decoded = decoder.parse(arbid, data)
        
        if decoded:
            stats["decoded"] += 1
            
            # ID-Statistik
            if arbid not in stats["by_id"]:
                stats["by_id"][arbid] = {"count": 0, "keys": set()}
            
            stats["by_id"][arbid]["count"] += 1
            stats["by_id"][arbid]["keys"].update(decoded.keys())
            
            # State mergen
            nonlocal state
            state = decoder.merge_state(state, decoded)
        
        else:
            stats["unknown"] += 1
    
    # Trace abspielen
    print("\nProcessing trace...")
    start = time.time()
    player.play(process_message)
    elapsed = time.time() - start
    
    # Ergebnisse
    print(f"\n{'=' * 70}")
    print("RESULTS")
    print("=" * 70)
    print(f"Processing time: {elapsed:.2f}s")
    print(f"Total messages:  {stats['total']}")
    print(f"Decoded:         {stats['decoded']} ({stats['decoded']/stats['total']*100:.1f}%)")
    print(f"Unknown:         {stats['unknown']}")
    
    print(f"\n{'=' * 70}")
    print("DECODED IDs")
    print("=" * 70)
    
    for arbid in sorted(stats["by_id"].keys()):
        info = stats["by_id"][arbid]
        count = info["count"]
        keys = sorted(info["keys"])
        keys_str = ", ".join(keys[:5])
        if len(keys) > 5:
            keys_str += f", ... (+{len(keys)-5} more)"
        
        print(f"0x{arbid:03X} ({count:5d}x): {keys_str}")
    
    print(f"\n{'=' * 70}")
    print("FINAL STATE")
    print("=" * 70)
    
    # Wichtige Werte anzeigen
    important_keys = [
        "speed_kmh", "power_kW", "soc_pct", "voltage_V", "current_A",
        "pack_temp_C", "range_km", "soh_pct", "is_enerdel",
        "gear", "mains_voltage_V", "charger_enabled"
    ]
    
    for key in important_keys:
        if key in state:
            value = state[key]
            if isinstance(value, float):
                print(f"  {key:25s} = {value:.2f}")
            else:
                print(f"  {key:25s} = {value}")
    
    print(f"\n{'=' * 70}")
    print("NEW/UNKNOWN DATA FIELDS")
    print("=" * 70)
    
    # Alle "_raw" Fields (noch zu analysieren)
    raw_fields = {k: v for k, v in state.items() if "_raw" in k or "diag" in k}
    for key, value in sorted(raw_fields.items()):
        print(f"  {key:30s} = {value}")
    
    print(f"\n{'=' * 70}")
    print(f"Battery Type: {decoder.get_battery_type()}")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_with_trace.py <trace_file.trc>")
        print("\nExample:")
        print("  python3 test_with_trace.py ../AKKU/191210_PCAN-Traces/191210_Arndt_Think_Laden_ab_91_procent.trc")
        sys.exit(1)
    
    test_decoder_with_trace(sys.argv[1])
