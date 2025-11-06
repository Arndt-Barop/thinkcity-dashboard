#!/usr/bin/env python3
"""Test script to check negative consumption (recuperation)."""

import sys
import time
from trip_computer import TripComputer

# Erstelle Trip Computer
tc = TripComputer()

# Test mit negativer Leistung
print("Testing NEGATIVE consumption (recuperation):")
print("=" * 60)

for i in range(5):
    state = {
        "speed_kmh": 50.0,
        "power_kW": -10.0,  # NEGATIVE Leistung = Rekuperation
        "soc_pct": 70.0
    }
    
    result = tc.update(state)
    
    print(f"Update {i+1}:")
    print(f"  Speed: {state['speed_kmh']} km/h")
    print(f"  Power: {state['power_kW']} kW (RECUPERATING)")
    print(f"  consumption_kwh_100km: {result.get('consumption_kwh_100km', 'NOT SET')}")
    print()
    
    time.sleep(0.1)

# Test mit positiver Leistung
print("\n" + "=" * 60)
print("Testing POSITIVE consumption (driving):")
print("=" * 60)

for i in range(5):
    state = {
        "speed_kmh": 50.0,
        "power_kW": 10.0,  # POSITIVE Leistung = Verbrauch
        "soc_pct": 70.0
    }
    
    result = tc.update(state)
    
    print(f"Update {i+1}:")
    print(f"  Speed: {state['speed_kmh']} km/h")
    print(f"  Power: {state['power_kW']} kW (CONSUMING)")
    print(f"  consumption_kwh_100km: {result.get('consumption_kwh_100km', 'NOT SET')}")
    print()
    
    time.sleep(0.1)
