#!/usr/bin/env python3
"""Test script to debug consumption calculation."""

import sys
import time
from trip_computer import TripComputer

# Erstelle Trip Computer
tc = TripComputer()

# Simuliere mehrere Updates
print("Testing consumption calculation:")
print("=" * 60)

for i in range(10):
    state = {
        "speed_kmh": 50.0,
        "power_kW": 10.0,  # Positive Leistung
        "soc_pct": 70.0
    }
    
    result = tc.update(state)
    
    print(f"Update {i+1}:")
    print(f"  Speed: {state['speed_kmh']} km/h")
    print(f"  Power: {state['power_kW']} kW")
    print(f"  consumption_now_wh_km: {tc.consumption_now_wh_km}")
    print(f"  consumption_now_kwh_100km: {tc.consumption_now_kwh_100km}")
    print(f"  Result consumption_kwh_100km: {result.get('consumption_kwh_100km', 'NOT SET')}")
    print(f"  Trip count: {tc.trip_count}")
    print()
    
    time.sleep(0.1)

print("=" * 60)
print("Final values:")
print(f"  consumption_now_wh_km: {tc.consumption_now_wh_km}")
print(f"  consumption_now_kwh_100km: {tc.consumption_now_kwh_100km}")
print(f"  trip_avg_consumption: {tc.trip_avg_consumption}")
