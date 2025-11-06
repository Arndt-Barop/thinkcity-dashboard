# trip_computer.py
# Berechnung von Range, Consumption, Trip-Statistiken
# Verbesserte Version with Welford-Algorithmus und Kalibrierung
# memoryt Statistiken persistent in Datenbank (Remanenz at hartem Abschalten)

import os
import time
from typing import Optional, Dict, Any

class TripComputer:
    """
    Calculates range, consumption und Trip-Statistiken.
    Basiert auf Original-BASIC-Code, aber erweitert.
    memoryt Gesamt-Durchschnitt persistent in Datenbank.
    """
    
    def __init__(self, db_manager=None):
        # Kalibrierbare Parameter (from Umgebungsvariablen oder Defaults)
        # WICHTIG: Degradierte Batterie - realistisch 17 kWh nutzbar (statt 24 kWh neu)
        self.battery_capacity_kwh = float(os.environ.get("TC_BATTERY_CAPACITY_KWH", "17.0"))
        self.default_consumption_wh_km = float(os.environ.get("TC_DEFAULT_CONSUMPTION_WH_KM", "150.0"))
        # Maximum range (safety limit for degraded battery)
        self.max_range_km = float(os.environ.get("TC_MAX_RANGE_KM", "100.0"))
        
        self.db_manager = db_manager
        
        # Trip-Daten (aktuell)
        self.trip_count = 0  # Anzahl Messungen
        self.trip_avg_consumption = 0.0  # Durchschnitt Wh/km
        self.trip_distance_km = 0.0
        self.trip_energy_kwh = 0.0
        self.trip_start_soc = None
        
        # Total data (across all trips) - loaded from DB
        self.total_count = 0
        self.total_avg_consumption = 0.0
        self.total_distance_km = 0.0
        self.total_energy_kwh = 0.0
        
        # Load saved Statistiken from Datenbank
        self._load_stats()
        
        # For distance calculation (integration)
        self.last_speed_kmh = 0.0
        self.last_time = time.time()
        
        # Aktuelle Werte (werden in update() gesetzt)
        self.consumption_now_wh_km = 0.0
        self.consumption_now_kwh_100km = 0.0
    
    def _load_stats(self):
        """Lädt gespeicherte Gesamt-Statistiken from der Datenbank (Remanenz)."""
        loaded = False
        
        # Load from database (main source for remanence on hard shutdown)
        if self.db_manager:
            try:
                stats = self.db_manager.get_latest_total_stats()
                if stats:
                    self.total_count = stats.get('total_count', 0)
                    self.total_avg_consumption = stats.get('total_avg_consumption', 0.0)
                    self.total_distance_km = stats.get('total_distance_km', 0.0)
                    self.total_energy_kwh = stats.get('total_energy_kwh', 0.0)
                    print(f"Loaded trip stats from DB: {self.total_count} samples, avg {self.total_avg_consumption:.1f} Wh/km")
                    loaded = True
            except Exception as e:
                print(f"Could not load trip stats from DB: {e}")
        
        if not loaded:
            print("No trip stats found in DB, starting fresh")
    
    def update(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualisiert Trip-Computer with neuem Zustand.
        Gibt erweiterten State with Range/Consumption zurück.
        """
        speed_kmh = state.get("speed_kmh", 0.0)
        power_kw = state.get("power_kW", 0.0)
        soc_pct = state.get("soc_pct", 0.0)
        
        current_time = time.time()
        delta_time_h = (current_time - self.last_time) / 3600.0  # Stunden
        
        # Distanz-Inkrement (Trapez-Integration)
        if delta_time_h > 0 and speed_kmh > 0:
            avg_speed = (speed_kmh + self.last_speed_kmh) / 2.0
            delta_distance_km = avg_speed * delta_time_h
            
            self.trip_distance_km += delta_distance_km
            self.total_distance_km += delta_distance_km
            
            # Energie-Inkrement (only at consumption, nicht Rekuperation)
            if power_kw > 0:
                delta_energy_kwh = power_kw * delta_time_h
                self.trip_energy_kwh += delta_energy_kwh
                self.total_energy_kwh += delta_energy_kwh
        
        # Aktueller consumption (only at Fahrt > 2 km/h)
        if speed_kmh > 2.0:
            self.consumption_now_wh_km = (power_kw * 1000.0) / speed_kmh
            
            # Welford algorithm for stable average (only positive values)
            if power_kw > 0:
                self.trip_count += 1
                self.trip_avg_consumption += (self.consumption_now_wh_km - self.trip_avg_consumption) / self.trip_count
                
                self.total_count += 1
                self.total_avg_consumption += (self.consumption_now_wh_km - self.total_avg_consumption) / self.total_count
        else:
            self.consumption_now_wh_km = 0.0
        
        # Konvertiere zu kWh/100km
        self.consumption_now_kwh_100km = self.consumption_now_wh_km / 10.0
        
        # Range-Berechnung
        range_km = self.calculate_range(soc_pct)
        
        # State erweitern
        state["consumption_now_wh_km"] = self.consumption_now_wh_km
        state["consumption_trip_wh_km"] = self.trip_avg_consumption
        state["consumption_total_wh_km"] = self.total_avg_consumption
        state["consumption_now_kwh_100km"] = self.consumption_now_kwh_100km
        state["consumption_kwh_100km"] = self.consumption_now_kwh_100km  # Alias for main screen
        state["consumption_trip_kwh_100km"] = self.total_avg_consumption / 10.0  # Zeige TOTAL statt TRIP
        state["consumption_total_kwh_100km"] = self.total_avg_consumption / 10.0
        state["range_km"] = range_km
        state["trip_distance_km"] = self.trip_distance_km
        state["trip_energy_kwh"] = self.trip_energy_kwh
        # For DB storage
        state["total_distance_km"] = self.total_distance_km
        state["total_energy_kwh"] = self.total_energy_kwh
        state["total_count"] = self.total_count
        
        # Daten werden automatisch in DB gespeichert durch dashboard.py _log_sample()
        # No separate storage needed anymore (remanence guaranteed by DB)
        
        # Update for next iteration
        self.last_speed_kmh = speed_kmh
        self.last_time = current_time
        
        return state
    
    def calculate_range(self, soc_pct: float) -> float:
        """
        Calculates verbleibende Reichweite in km.
        
        Range = (SOC/100) × Kapazität × 1000 / Durchschnittsverbrauch
        Begrenzt auf max_range_km (100km für degradierte Batterie)
        """
        # Nutze Trip-Durchschnitt if vorhanden, sonst Default
        if self.trip_count > 10:  # Min. 10 measurements for validity
            avg_consumption = self.trip_avg_consumption
        elif self.total_count > 10:
            avg_consumption = self.total_avg_consumption
        else:
            avg_consumption = self.default_consumption_wh_km
        
        # Verhindere Division durch Null
        if avg_consumption < 10.0:
            avg_consumption = self.default_consumption_wh_km
        
        available_energy_kwh = (soc_pct / 100.0) * self.battery_capacity_kwh
        range_km = (available_energy_kwh * 1000.0) / avg_consumption
        
        # Begrenze auf realistisches Maximum (degradierte Batterie)
        range_km = min(range_km, self.max_range_km)
        
        return max(0.0, range_km)
    
    def reset_trip(self):
        """Setzt Trip-Zähler zurück (aber nicht Gesamt-Statistik)."""
        self.trip_count = 0
        self.trip_avg_consumption = 0.0
        self.trip_distance_km = 0.0
        self.trip_energy_kwh = 0.0
        self.trip_start_soc = None
    
    def reset_total_stats(self):
        """Setzt Gesamt-Statistiken zurück (durchschnittlicher consumption)."""
        self.total_count = 0
        self.total_avg_consumption = 0.0
        self.total_distance_km = 0.0
        self.total_energy_kwh = 0.0
        # Values will be stored as 0 in next DB sample write
        print("Total trip statistics reset")
    
    def start_trip(self, soc_pct: float):
        """Startet neuen Trip (z.B. at Zündung an)."""
        self.reset_trip()
        self.trip_start_soc = soc_pct
    
    def end_trip(self, soc_pct: float) -> Dict[str, Any]:
        """
        Beendet Trip und gibt Zusammenfassung zurück.
        """
        return {
            "start_soc": self.trip_start_soc,
            "end_soc": soc_pct,
            "distance_km": self.trip_distance_km,
            "energy_kwh": self.trip_energy_kwh,
            "avg_consumption_wh_km": self.trip_avg_consumption,
            "avg_consumption_kwh_100km": self.trip_avg_consumption / 10.0,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt aktuelle Statistiken zurück."""
        return {
            "trip": {
                "count": self.trip_count,
                "avg_consumption_wh_km": self.trip_avg_consumption,
                "distance_km": self.trip_distance_km,
                "energy_kwh": self.trip_energy_kwh,
            },
            "total": {
                "count": self.total_count,
                "avg_consumption_wh_km": self.total_avg_consumption,
                "distance_km": self.total_distance_km,
                "energy_kwh": self.total_energy_kwh,
            },
            "config": {
                "battery_capacity_kwh": self.battery_capacity_kwh,
                "default_consumption_wh_km": self.default_consumption_wh_km,
            }
        }
    
    def shutdown(self):
        """Cleanup atm Herunterfahren (DB-memoryung erfolgt automatisch)."""
        print("TripComputer shutdown - statistics persisted in database")
