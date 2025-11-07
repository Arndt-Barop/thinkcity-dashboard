# soh_tracker.py
# State of Health (SOH) Tracking mit Exponential Smoothing
# Speichert SOH persistent in Datenbank (Remanenz bei hartem Abschalten)

import time
from typing import Optional, Dict, Any

class SOHTracker:
    """
    Tracks State of Health (SOH) über Zeit mit Exponential Smoothing.
    Analog zum TripComputer, aber für Batterie-Gesundheit.
    
    SOH wird aus dem Zellspannungs-Delta (e_pack_delta_cell_V) geschätzt
    und langsam über Zeit angepasst (nicht springend).
    """
    
    def __init__(self, db_manager=None, initial_soh: float = 100.0):
        self.db_manager = db_manager
        
        # Smoothing parameter (0.001 = very slow adaptation)
        # Das bedeutet: 0.1% Anpassung pro Update
        # Bei 1 Update/Sekunde dauert es ~1000 Sekunden für 1% Änderung
        self.alpha = 0.001
        
        # Minimum change to trigger DB save (avoid excessive writes)
        self.min_delta_for_save = 0.5  # 0.5%
        
        # Current smoothed SOH value
        self.soh_pct = initial_soh
        self.last_saved_soh = initial_soh
        
        # Load saved SOH from database
        self._load_soh()
        
        # Track when we last got valid data
        self.last_update_time = time.time()
        self.update_count = 0
    
    def _load_soh(self):
        """Lädt gespeicherten SOH aus der Datenbank."""
        if self.db_manager:
            try:
                soh = self.db_manager.get_latest_soh()
                if soh is not None and 70.0 <= soh <= 100.0:
                    self.soh_pct = soh
                    self.last_saved_soh = soh
                    print(f"Loaded SOH from DB: {soh:.1f}%")
                else:
                    print(f"No valid SOH in DB, starting with {self.soh_pct:.1f}%")
            except Exception as e:
                print(f"Could not load SOH from DB: {e}")
    
    def update(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates SOH based on current CAN data.
        Uses exponential smoothing to prevent jumping values.
        
        Args:
            state: Current CAN state dict with 'e_pack_delta_cell_V' and 'soh_pct_instant'
        
        Returns:
            Updated state dict with smoothed 'soh_pct'
        """
        # Get instantaneous SOH (calculated from current delta)
        instant_soh = state.get("soh_pct")
        
        if instant_soh is None:
            # No data available - return current smoothed value
            state["soh_pct"] = self.soh_pct
            return state
        
        # Validate instant_soh range
        if not (70.0 <= instant_soh <= 100.0):
            # Invalid value - keep current
            state["soh_pct"] = self.soh_pct
            return state
        
        # Apply exponential smoothing
        # new_soh = old_soh * (1 - alpha) + instant_soh * alpha
        self.soh_pct = self.soh_pct * (1.0 - self.alpha) + instant_soh * self.alpha
        
        # Clamp to valid range
        self.soh_pct = max(70.0, min(100.0, self.soh_pct))
        
        # Update state with smoothed value
        state["soh_pct"] = self.soh_pct
        state["soh_pct_instant"] = instant_soh  # Keep instant for debugging
        
        self.update_count += 1
        self.last_update_time = time.time()
        
        # SOH wird automatisch in DB gespeichert durch dashboard.py _log_sample()
        # (wie auch consumption - keine separate Speicherung mehr nötig)
        
        return state
    
    def reset_soh(self, new_soh: float = 100.0):
        """
        Resets SOH to specified value (e.g. after battery replacement).
        Default: 100% (new battery)
        """
        if 70.0 <= new_soh <= 100.0:
            self.soh_pct = new_soh
            self.last_saved_soh = new_soh
            print(f"SOH reset to {new_soh:.1f}%")
        else:
            print(f"Invalid SOH value: {new_soh}%. Must be between 70% and 100%")
    
    def get_stats(self) -> Dict[str, Any]:
        """Returns current SOH statistics."""
        return {
            "soh_pct": self.soh_pct,
            "update_count": self.update_count,
            "alpha": self.alpha,
            "last_update": self.last_update_time
        }
    
    def shutdown(self):
        """Cleanup beim Herunterfahren (DB-Speicherung erfolgt automatisch)."""
        print(f"SOHTracker shutdown - SOH: {self.soh_pct:.1f}% persisted in database")
