# db_manager.py
# Datenbank-Manager mit Trip-Auto-Detection und GPS-Support

import sqlite3
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DBManager:
    """
    SQLite-Datenbank-Manager für ThinkCity Dashboard.
    
    Features:
    - Auto-Trip-Detection (Start bei Bewegung, Ende nach 5min Idle)
    - GPS-ready (latitude/longitude Spalten)
    - Sync-Status für WLAN-Upload
    """
    
    def __init__(self, db_path: Optional[str] = None):
        # DB-Pfad aus Env oder Fallback
        if db_path is None:
            db_path = os.getenv("TC_DB_PATH", "/mnt/usbssd/thinkcity.db")
        
        self.db_path = db_path
        self.current_trip_id: Optional[int] = None
        self.last_sample_time: Optional[datetime] = None
        self.trip_idle_timeout: float = 300.0  # 5 Minuten
        
        # Erstelle DB falls nicht vorhanden
        self._init_db()
    
    @contextmanager
    def _get_conn(self):
        """Context manager für DB-Verbindungen."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Erstellt Tabellen falls nicht vorhanden."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Trips Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    start_odo_km REAL,
                    end_odo_km REAL,
                    distance_km REAL,
                    avg_consumption_wh_km REAL,
                    avg_consumption_kwh_100km REAL,
                    start_soc_pct REAL,
                    end_soc_pct REAL,
                    energy_used_kwh REAL,
                    max_power_kw REAL,
                    min_power_kw REAL,
                    avg_speed_kmh REAL,
                    max_speed_kmh REAL,
                    synced INTEGER DEFAULT 0
                )
            """)
            
            # Samples Tabelle (Messdaten)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS samples (
                    sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trip_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    speed_kmh REAL,
                    soc_pct REAL,
                    voltage_V REAL,
                    current_A REAL,
                    power_kW REAL,
                    pack_temp_C REAL,
                    ambient_temp_C REAL,
                    latitude REAL,
                    longitude REAL,
                    consumption_wh_km REAL,
                    consumption_total_wh_km REAL,
                    total_distance_km REAL,
                    total_energy_kwh REAL,
                    total_count INTEGER,
                    range_km REAL,
                    synced INTEGER DEFAULT 0,
                    FOREIGN KEY (trip_id) REFERENCES trips (trip_id)
                )
            """)
            
            # Migration: Add new columns if not present
            cursor.execute("PRAGMA table_info(samples)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if "consumption_total_wh_km" not in columns:
                cursor.execute("ALTER TABLE samples ADD COLUMN consumption_total_wh_km REAL")
                logger.info("Added consumption_total_wh_km column to samples table")
            
            if "total_distance_km" not in columns:
                cursor.execute("ALTER TABLE samples ADD COLUMN total_distance_km REAL")
                logger.info("Added total_distance_km column to samples table")
            
            if "total_energy_kwh" not in columns:
                cursor.execute("ALTER TABLE samples ADD COLUMN total_energy_kwh REAL")
                logger.info("Added total_energy_kwh column to samples table")
            
            if "total_count" not in columns:
                cursor.execute("ALTER TABLE samples ADD COLUMN total_count INTEGER")
                logger.info("Added total_count column to samples table")
            
            # Index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_samples_trip 
                ON samples(trip_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_samples_timestamp 
                ON samples(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_trips_synced 
                ON trips(synced)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_samples_synced 
                ON samples(synced)
            """)
            
            logger.info(f"Database initialized at {self.db_path}")
    
    def start_trip(self, odo_km: float, soc_pct: float) -> int:
        """
        Startet einen neuen Trip.
        Gibt trip_id zurück.
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trips (start_time, start_odo_km, start_soc_pct)
                VALUES (?, ?, ?)
            """, (datetime.now().isoformat(), odo_km, soc_pct))
            
            trip_id = cursor.lastrowid
            self.current_trip_id = trip_id
            self.last_sample_time = datetime.now()
            
            logger.info(f"Started trip {trip_id}")
            return trip_id
    
    def end_trip(
        self,
        odo_km: float,
        soc_pct: float,
        avg_consumption_wh_km: float,
        avg_consumption_kwh_100km: float,
        stats: Optional[Dict[str, float]] = None
    ):
        """Beendet den aktuellen Trip."""
        if self.current_trip_id is None:
            logger.warning("No active trip to end")
            return
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Hole Start-Daten
            cursor.execute(
                "SELECT start_odo_km FROM trips WHERE trip_id = ?",
                (self.current_trip_id,)
            )
            row = cursor.fetchone()
            if not row:
                logger.error(f"Trip {self.current_trip_id} not found")
                return
            
            start_odo = row[0]
            distance_km = odo_km - start_odo
            
            # Stats mit Defaults
            if stats is None:
                stats = {}
            
            cursor.execute("""
                UPDATE trips SET
                    end_time = ?,
                    end_odo_km = ?,
                    distance_km = ?,
                    end_soc_pct = ?,
                    avg_consumption_wh_km = ?,
                    avg_consumption_kwh_100km = ?,
                    max_power_kw = ?,
                    min_power_kw = ?,
                    avg_speed_kmh = ?,
                    max_speed_kmh = ?
                WHERE trip_id = ?
            """, (
                datetime.now().isoformat(),
                odo_km,
                distance_km,
                soc_pct,
                avg_consumption_wh_km,
                avg_consumption_kwh_100km,
                stats.get("max_power_kw", 0.0),
                stats.get("min_power_kw", 0.0),
                stats.get("avg_speed_kmh", 0.0),
                stats.get("max_speed_kmh", 0.0),
                self.current_trip_id
            ))
            
            logger.info(f"Ended trip {self.current_trip_id}: {distance_km:.2f} km")
            self.current_trip_id = None
            self.last_sample_time = None
        
        # Cleanup old trips (only synced, older than 90 days)
        self.cleanup_old_trips(days=90)
    
    def add_sample(self, data: Dict[str, Any]):
        """
        Fügt Sample hinzu.
        Handled Auto-Trip-Detection.
        """
        now = datetime.now()
        
        # Trip Auto-Start bei Bewegung
        speed = data.get("speed_kmh", 0.0)
        
        if self.current_trip_id is None and speed > 1.0:
            # Starte neuen Trip
            self.start_trip(
                odo_km=data.get("odo_km", 0.0),
                soc_pct=data.get("soc_pct", 0.0)
            )
        
        # Trip Auto-End nach Idle
        if self.current_trip_id is not None and self.last_sample_time is not None:
            idle_seconds = (now - self.last_sample_time).total_seconds()
            
            if speed < 1.0 and idle_seconds > self.trip_idle_timeout:
                # Beende Trip
                self.end_trip(
                    odo_km=data.get("odo_km", 0.0),
                    soc_pct=data.get("soc_pct", 0.0),
                    avg_consumption_wh_km=data.get("consumption_wh_km", 0.0),
                    avg_consumption_kwh_100km=data.get("consumption_kwh_100km", 0.0)
                )
                return  # Kein Sample bei Idle
        
        # Insert sample (only with active trip)
        if self.current_trip_id is not None:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO samples (
                        trip_id, timestamp, speed_kmh, soc_pct,
                        voltage_V, current_A, power_kW, pack_temp_C,
                        ambient_temp_C, latitude, longitude,
                        consumption_wh_km, consumption_total_wh_km,
                        total_distance_km, total_energy_kwh, total_count,
                        range_km
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.current_trip_id,
                    now.isoformat(),
                    data.get("speed_kmh", 0.0),
                    data.get("soc_pct", 0.0),
                    data.get("voltage_V", 0.0),
                    data.get("current_A", 0.0),
                    data.get("power_kW", 0.0),
                    data.get("pack_temp_C", 0.0),
                    data.get("ambient_temp_C", 0.0),
                    data.get("latitude"),
                    data.get("longitude"),
                    data.get("consumption_wh_km", 0.0),
                    data.get("consumption_total_wh_km", 0.0),
                    data.get("total_distance_km", 0.0),
                    data.get("total_energy_kwh", 0.0),
                    data.get("total_count", 0),
                    data.get("range_km", 0.0)
                ))
            
            self.last_sample_time = now
    
    def get_unsynced_trips(self) -> List[Dict[str, Any]]:
        """Gibt alle nicht synchronisierten Trips zurück."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM trips 
                WHERE synced = 0 AND end_time IS NOT NULL
                ORDER BY start_time ASC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_trip_samples(self, trip_id: int) -> List[Dict[str, Any]]:
        """Gibt alle Samples eines Trips zurück."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM samples 
                WHERE trip_id = ?
                ORDER BY timestamp ASC
            """, (trip_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_trip_synced(self, trip_id: int):
        """Markiert Trip als synchronisiert."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE trips SET synced = 1 WHERE trip_id = ?",
                (trip_id,)
            )
            cursor.execute(
                "UPDATE samples SET synced = 1 WHERE trip_id = ?",
                (trip_id,)
            )
            
            logger.info(f"Marked trip {trip_id} as synced")
    
    def get_latest_total_stats(self) -> Optional[Dict[str, Any]]:
        """
        Holt die neuesten Total-statistics aus der DB.
        Wird beim Start verwendet um Remanenz zu gewährleisten.
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT consumption_total_wh_km, total_distance_km, 
                       total_energy_kwh, total_count
                FROM samples 
                WHERE consumption_total_wh_km IS NOT NULL 
                  AND total_count > 0
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_avg_consumption': row[0] or 0.0,
                    'total_distance_km': row[1] or 0.0,
                    'total_energy_kwh': row[2] or 0.0,
                    'total_count': row[3] or 0
                }
            return None
    
    def get_lifetime_stats(self) -> Dict[str, Any]:
        """Berechnet Lifetime-statistics."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as trip_count,
                    SUM(distance_km) as total_km,
                    AVG(avg_consumption_kwh_100km) as avg_consumption,
                    SUM(energy_used_kwh) as total_energy_kwh
                FROM trips
                WHERE end_time IS NOT NULL
            """)
            
            row = cursor.fetchone()
            
            return {
                "trip_count": row["trip_count"] or 0,
                "total_km": row["total_km"] or 0.0,
                "avg_consumption_kwh_100km": row["avg_consumption"] or 0.0,
                "total_energy_kwh": row["total_energy_kwh"] or 0.0
            }
    
    def cleanup_old_trips(self, days: int = 90):
        """
        Löscht Trips älter als X Tage (nur wenn synced).
        
        Args:
            days: Alter in Tagen (Standard: 90)
        
        Returns:
            Tuple[int, int]: (gelöschte Trips, gelöschte Samples)
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Count affected entries
            cursor.execute("""
                SELECT COUNT(*) FROM trips 
                WHERE synced = 1 AND end_time < ?
            """, (cutoff.isoformat(),))
            trips_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM samples WHERE trip_id IN (
                    SELECT trip_id FROM trips 
                    WHERE synced = 1 AND end_time < ?
                )
            """, (cutoff.isoformat(),))
            samples_count = cursor.fetchone()[0]
            
            # Delete samples first (Foreign Key)
            cursor.execute("""
                DELETE FROM samples WHERE trip_id IN (
                    SELECT trip_id FROM trips 
                    WHERE synced = 1 AND end_time < ?
                )
            """, (cutoff.isoformat(),))
            
            # Delete trips
            cursor.execute("""
                DELETE FROM trips 
                WHERE synced = 1 AND end_time < ?
            """, (cutoff.isoformat(),))
            
            if trips_count > 0:
                logger.info(
                    f"Cleaned up {trips_count} trips and {samples_count} samples "
                    f"older than {days} days"
                )
            
            return trips_count, samples_count
    
    def vacuum(self):
        """VACUUM für Wartung."""
        with self._get_conn() as conn:
            conn.execute("VACUUM")
            logger.info("Database vacuumed")


# CLI Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing DBManager...")
    
    # Init mit Test-DB
    db = DBManager("/tmp/test_thinkcity.db")
    
    # Simuliere Trip
    print("\n1. Starting trip...")
    db.start_trip(odo_km=12345.0, soc_pct=85.0)
    
    print("2. Adding samples...")
    for i in range(5):
        db.add_sample({
            "speed_kmh": 50.0 + i * 5,
            "soc_pct": 85.0 - i * 2,
            "voltage_V": 330.0,
            "current_A": -20.0,
            "power_kW": -6.6,
            "pack_temp_C": 25.0,
            "consumption_wh_km": 150.0,
            "range_km": 120.0 - i * 10,
            "odo_km": 12345.0 + i * 0.5
        })
    
    print("3. Ending trip...")
    db.end_trip(
        odo_km=12347.5,
        soc_pct=77.0,
        avg_consumption_wh_km=150.0,
        avg_consumption_kwh_100km=15.0,
        stats={"max_power_kw": -8.5, "max_speed_kmh": 75.0}
    )
    
    print("\n4. Lifetime stats:")
    stats = db.get_lifetime_stats()
    print(f"   Trips: {stats['trip_count']}")
    print(f"   Total: {stats['total_km']:.1f} km")
    print(f"   Avg: {stats['avg_consumption_kwh_100km']:.1f} kWh/100km")
    
    print("\nTest complete!")
