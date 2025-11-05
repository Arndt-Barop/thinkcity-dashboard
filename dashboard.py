# dashboard.py
# Haupt-Dashboard-Anwendung für ThinkCity

import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from can_interface import CANInterface
from can_decoder import CANDecoder
from db_manager import DBManager
from trip_computer import TripComputer
from main_screen import MainScreen
from battery_screen import BatteryScreen
from charge_screen import ChargeScreen
from cell_voltages_screen import CellVoltagesScreen
from raw_data_screen import RawDataScreen
from settings_screen import SettingsScreen
from widgets import TouchButton
from translations import get_translator

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ThinkCityDashboard(QWidget):
    """
    Haupt-Dashboard-Anwendung.
    
    Features:
    - CAN-Bus Integration
    - 3 Screens (Main, Battery, Charge)
    - Auto-Logging
    - Trip-Computer
    """
    
    def __init__(self):
        super().__init__()
        
        # Translation
        self.translator = get_translator()
        
        # Config laden
        self.config = self._load_config()
        
        # State
        self.state: Dict[str, Any] = {}
        self.last_update_time: Optional[datetime] = None
        
        # Module
        self.can_interface: Optional[CANInterface] = None
        self.can_decoder = CANDecoder()
        self.db_manager = DBManager()
        self.trip_computer = TripComputer()
        
        # Odometer-Simulation (wird später aus Geschwindigkeit integriert)
        self.odo_km = 0.0
        self.last_speed_update = datetime.now()
        
        # UI
        self._init_ui()
        
        # CAN-Bus connect (async)
        QTimer.singleShot(500, self._connect_can)
        
        # Update-Timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_loop)
        self.update_timer.start(100)  # 10 Hz
        
        # Logging-Timer (konfigurierbar)
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self._log_sample)
        log_interval_ms = self.config.get("logging_interval_sec", 1) * 1000
        self.log_timer.start(log_interval_ms)
    
    def _load_config(self):
        """Lädt Konfiguration aus JSON."""
        import json
        config_file = os.path.expanduser("~/thinkcity-dashboard-v3/config.json")
        
        defaults = {
            "logging_enabled": True,
            "logging_interval_sec": 1,
            "logging_fields": [
                "speed_kmh", "soc_pct", "voltage_V", "current_A", "power_kW",
                "pack_temp_C", "ambient_temp_C", "consumption_wh_km", "range_km",
                "odo_km", "latitude", "longitude"
            ]
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except Exception as e:
                logger.warning(f"Config load error: {e}")
        
        return defaults
    
    def _init_ui(self):
        """Erstellt UI-Layout."""
        self.setWindowTitle("ThinkCity Dashboard v3")
        
        # Fullscreen für Pi
        if os.getenv("TC_FULLSCREEN", "1") == "1":
            self.setGeometry(0, 0, 1280, 800)  # Force size before fullscreen (linuxfb fix)
            self.showFullScreen()
        else:
            self.resize(1280, 800)  # SunFounder 10" Display
        
        # Hintergrund
        self.setStyleSheet("background-color: #1a1a1a;")
        
        # Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Stacked Widget für Screens
        self.screen_stack = QStackedWidget()
        
        self.main_screen = MainScreen()
        self.battery_screen = BatteryScreen()
        self.charge_screen = ChargeScreen()
        self.cell_voltages_screen = CellVoltagesScreen()
        self.raw_data_screen = RawDataScreen()
        self.settings_screen = SettingsScreen()
        
        self.screen_stack.addWidget(self.main_screen)           # Index 0
        self.screen_stack.addWidget(self.battery_screen)        # Index 1
        self.screen_stack.addWidget(self.charge_screen)         # Index 2
        self.screen_stack.addWidget(self.cell_voltages_screen)  # Index 3
        self.screen_stack.addWidget(self.raw_data_screen)       # Index 4
        self.screen_stack.addWidget(self.settings_screen)       # Index 5
        
        # Settings-Signal verbinden
        self.settings_screen.settings_changed.connect(self._on_settings_changed)
        
        main_layout.addWidget(self.screen_stack, stretch=1)
        
        # Navigation-Buttons (unten)
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(5)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        
        t = self.translator.get
        
        self.btn_main = TouchButton(t("main"))
        self.btn_main.set_callback(lambda: self._switch_screen(0))
        nav_layout.addWidget(self.btn_main)
        
        self.btn_battery = TouchButton(t("battery"))
        self.btn_battery.set_callback(lambda: self._switch_screen(1))
        nav_layout.addWidget(self.btn_battery)
        
        self.btn_cells = TouchButton(t("cells"))
        self.btn_cells.set_callback(lambda: self._switch_screen(3))
        nav_layout.addWidget(self.btn_cells)
        
        self.btn_charge = TouchButton(t("charge"))
        self.btn_charge.set_callback(lambda: self._switch_screen(2))
        nav_layout.addWidget(self.btn_charge)
        
        self.btn_raw = TouchButton(t("raw"))
        self.btn_raw.set_callback(lambda: self._switch_screen(4))
        nav_layout.addWidget(self.btn_raw)
        
        self.btn_settings = TouchButton("⚙️")
        self.btn_settings.set_callback(lambda: self._switch_screen(5))
        nav_layout.addWidget(self.btn_settings)
        
        main_layout.addLayout(nav_layout)
        
        self.setLayout(main_layout)
    
    def _connect_can(self):
        """Verbindet zum CAN-Bus."""
        logger.info("Connecting to CAN bus...")
        
        channel = os.getenv("TC_CAN_CHANNEL", "can0")
        self.can_interface = CANInterface(channel=channel)
        
        if not self.can_interface.connect():
            logger.error("Failed to connect to CAN bus - running in demo mode")
            self.can_interface = None
            # Demo-Daten-Timer starten
            self._start_demo_mode()
        else:
            # Prüfe ob vcan (Simulation) oder echtes CAN
            logger.info(f"Connected to {channel}")
    
    def _is_simulation_active(self):
        """Prüft ob CAN-Simulation aktiv ist (vcan)."""
        if self.can_interface is None:
            return True  # Demo-Modus = Simulation
        
        channel = os.getenv("TC_CAN_CHANNEL", "can0")
        return channel.startswith("vcan")
    
    def _is_wifi_connected(self):
        """Prüft ob WLAN verbunden ist."""
        import subprocess
        try:
            # Prüfe ob wlan0 eine IP hat
            result = subprocess.run(
                ["ip", "addr", "show", "wlan0"],
                capture_output=True,
                text=True,
                timeout=1
            )
            # Wenn "inet " in der Ausgabe ist, dann ist WLAN verbunden
            return "inet " in result.stdout
        except Exception:
            return False
    
    def _start_demo_mode(self):
        """Startet Demo-Modus mit Fake-Daten."""
        logger.info("Starting demo mode with fake data")
        
        def generate_demo_data():
            import random
            
            # Power meistens positiv (Verbrauch), manchmal negativ (Rekuperation)
            power = random.uniform(-5, 15) if random.random() > 0.3 else random.uniform(-15, -2)
            
            self.state.update({
                "speed_kmh": random.uniform(40, 80),
                "power_kW": power,
                "soc_pct": random.uniform(60, 90),
                "voltage_V": random.uniform(320, 340),
                "current_A": random.uniform(-30, 5),
                "pack_temp_C": random.uniform(20, 30),
                "pcu_ambient_temp_C": random.uniform(15, 25),
                "dod_pct": 100 - self.state.get("soc_pct", 70),
                "is_enerdel": True,
                "e_pack_min_cell_V": 3.45,
                "e_pack_max_cell_V": 3.50,
                "e_pack_avg_cell_V": 3.47,
                "e_pack_delta_cell_V": 0.05,
            })
            
            # Trip-Computer update - benutzt Return-Value
            self.state = self.trip_computer.update(self.state)
            
            # SOH
            self.state["soh_pct"] = 92.5
        
        demo_timer = QTimer()
        demo_timer.timeout.connect(generate_demo_data)
        demo_timer.start(100)
    
    def _update_loop(self):
        """Haupt-Update-Loop (10 Hz)."""
        if self.can_interface:
            # CAN-Messages lesen
            msg = self.can_interface.receive(timeout=0.01)
            
            if msg:
                # Rohdaten an Raw-Data-Screen weiterleiten
                self.raw_data_screen.add_can_frame(
                    msg.arbitration_id,
                    msg.data,
                    datetime.now()
                )
                
                # Dekodieren
                decoded = self.can_decoder.parse(msg.arbitration_id, msg.data)
                
                if decoded:
                    # State mergen
                    self.state = self.can_decoder.merge_state(self.state, decoded)
                    
                    # Odometer aus Speed integrieren
                    self._update_odometer()
                    
                    # Trip-Computer update - benutzt Return-Value
                    self.state = self.trip_computer.update(self.state)
                    self.last_update_time = datetime.now()
        
        # UI Updates (nur aktiver Screen)
        self._update_current_screen()
    
    def _update_odometer(self):
        """Berechnet Odometer aus Geschwindigkeit."""
        now = datetime.now()
        dt = (now - self.last_speed_update).total_seconds()
        
        speed_kmh = self.state.get("speed_kmh", 0.0)
        distance_km = (speed_kmh / 3600.0) * dt
        
        self.odo_km += distance_km
        self.state["odo_km"] = self.odo_km
        
        self.last_speed_update = now
    
    def _update_current_screen(self):
        """Updated nur den aktuell sichtbaren Screen."""
        current_idx = self.screen_stack.currentIndex()
        
        # WLAN- und Simulation-Status ermitteln
        wifi_status = self._is_wifi_connected()
        simulation_status = self._is_simulation_active()
        
        # Status an alle StatusBars weitergeben (nur aktueller Screen wird gerendert)
        screens_with_statusbar = [
            self.main_screen,
            self.battery_screen,
            self.charge_screen,
            self.cell_voltages_screen,
            self.raw_data_screen,
            self.settings_screen
        ]
        
        for screen in screens_with_statusbar:
            if hasattr(screen, 'status_bar'):
                screen.status_bar.set_wifi_status(wifi_status)
                screen.status_bar.set_simulation_status(simulation_status)
        
        # Screen-spezifische Updates
        if current_idx == 0:
            self.main_screen.update_data(self.state)
        elif current_idx == 1:
            self.battery_screen.update_data(self.state)
        elif current_idx == 2:
            self.charge_screen.update_data(self.state)
        elif current_idx == 3:
            self.cell_voltages_screen.update(self.state)
        elif current_idx == 4:
            self.raw_data_screen.update(self.state)
    
    def _log_sample(self):
        """Loggt Sample in DB (konfigurierbares Intervall)."""
        # Prüfe ob Logging aktiviert
        if not self.config.get("logging_enabled", True):
            return
        
        # Nur wenn genug Daten
        if len(self.state) < 5:
            return
        
        # Filtere Datenpunkte basierend auf Konfiguration
        selected_fields = self.config.get("logging_fields", [])
        
        if selected_fields:
            # Nur ausgewählte Felder loggen
            filtered_data = {
                key: value for key, value in self.state.items()
                if key in selected_fields or key == "odo_km"  # odo_km immer dabei
            }
        else:
            # Alle Felder loggen (Fallback)
            filtered_data = self.state
        
        self.db_manager.add_sample(filtered_data)
    
    def _switch_screen(self, index: int):
        """Wechselt zu anderem Screen."""
        self.screen_stack.setCurrentIndex(index)
        logger.info(f"Switched to screen {index}")
    
    def _on_settings_changed(self, new_config: dict):
        """Handle Settings-Änderungen."""
        logger.info("Settings changed, updating configuration...")
        
        # Config aktualisieren
        self.config.update(new_config)
        
        # Prüfe ob Sprache geändert wurde
        if "language" in new_config:
            logger.info(f"Language changed to {new_config['language']}")
            self.translator.set_language(new_config['language'])
            # Reload alle Screens
            self._reload_all_screens()
        
        # Logging-Timer Intervall anpassen
        log_interval_ms = new_config.get("logging_interval_sec", 1) * 1000
        if self.log_timer.interval() != log_interval_ms:
            self.log_timer.stop()
            self.log_timer.start(log_interval_ms)
            logger.info(f"Logging interval updated to {log_interval_ms}ms")
    
    def _reload_all_screens(self):
        """Lädt alle Screens neu nach Sprachwechsel."""
        logger.info("Reloading all screens with new language...")
        
        # Aktuellen Screen-Index merken
        current_index = self.screen_stack.currentIndex()
        
        # Alle Screens aus Stack entfernen
        while self.screen_stack.count() > 0:
            widget = self.screen_stack.widget(0)
            self.screen_stack.removeWidget(widget)
            widget.deleteLater()
        
        # Screens neu erstellen
        self.main_screen = MainScreen()
        self.battery_screen = BatteryScreen()
        self.charge_screen = ChargeScreen()
        self.cell_voltages_screen = CellVoltagesScreen()
        self.raw_data_screen = RawDataScreen()
        self.settings_screen = SettingsScreen()
        
        self.screen_stack.addWidget(self.main_screen)           # Index 0
        self.screen_stack.addWidget(self.battery_screen)        # Index 1
        self.screen_stack.addWidget(self.charge_screen)         # Index 2
        self.screen_stack.addWidget(self.cell_voltages_screen)  # Index 3
        self.screen_stack.addWidget(self.raw_data_screen)       # Index 4
        self.screen_stack.addWidget(self.settings_screen)       # Index 5
        
        # Settings-Signal neu verbinden
        self.settings_screen.settings_changed.connect(self._on_settings_changed)
        
        # Navigation-Buttons aktualisieren
        t = self.translator.get
        self.btn_main.setText(t("main"))
        self.btn_battery.setText(t("battery"))
        self.btn_cells.setText(t("cells"))
        self.btn_charge.setText(t("charge"))
        self.btn_raw.setText(t("raw"))
        
        # Zurück zum vorherigen Screen
        self.screen_stack.setCurrentIndex(current_index)
        
        logger.info("All screens reloaded successfully")
    
    def closeEvent(self, event):
        """Cleanup beim Schließen."""
        logger.info("Shutting down...")
        
        # Trip-Computer Statistiken speichern
        self.trip_computer.shutdown()
        
        # CAN-Bus schließen
        if self.can_interface:
            self.can_interface.shutdown()
        
        # Aktiven Trip beenden
        if self.db_manager.current_trip_id:
            self.db_manager.end_trip(
                odo_km=self.odo_km,
                soc_pct=self.state.get("soc_pct", 0.0),
                avg_consumption_wh_km=self.trip_computer.consumption_trip_wh_km,
                avg_consumption_kwh_100km=self.trip_computer.consumption_trip_kwh_100km
            )
        
        # DB schließen
        self.db_manager.vacuum()
        
        event.accept()


def main():
    """Haupt-Einstiegspunkt."""
    
    # Qt Platform Plugin (aus Env oder Default)
    platform = os.getenv("QT_QPA_PLATFORM", "xcb")  # xcb = minimal X11
    os.environ["QT_QPA_PLATFORM"] = platform
    
    logger.info(f"Starting ThinkCity Dashboard v3 (QT_QPA_PLATFORM={platform})")
    
    app = QApplication(sys.argv)
    
    # Cursor verstecken auf Pi
    if os.getenv("TC_HIDE_CURSOR", "0") == "1":
        app.setOverrideCursor(Qt.BlankCursor)
    
    dashboard = ThinkCityDashboard()
    dashboard.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
