# main_screen.py
# Hauptansicht: Geschwindigkeit, Power, SOC, Reichweite, Verbrauch

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from widgets import PowerGauge, DigitalDisplay, BatteryBar, StatusBar, GearDisplay
from translations import get_translator


class MainScreen(QWidget):
    """
    Hauptbildschirm des Dashboards.
    
    Layout:
    - Oben: Geschwindigkeit (groß)
    - Mitte: Power Gauge
    - Unten Links: Reichweite, Verbrauch
    - Unten Rechts: SOC-Balken
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = get_translator()
        self._init_ui()
    
    def _init_ui(self):
        """Erstellt UI-Layout."""
        t = self.translator.get
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # ====== Status-Bar (Datum, Uhrzeit, Temp) ======
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # ====== Obere Zeile: Geschwindigkeit + Fahrmodus ======
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        # Geschwindigkeit (links, groß)
        speed_layout = QVBoxLayout()
        self.speed_label = QLabel("0")
        self.speed_label.setAlignment(Qt.AlignCenter)
        font_speed = QFont("Arial", 80, QFont.Bold)
        self.speed_label.setFont(font_speed)
        self.speed_label.setStyleSheet("color: #00ffcc;")
        speed_layout.addWidget(self.speed_label)
        
        speed_unit = QLabel("km/h")
        speed_unit.setAlignment(Qt.AlignCenter)
        speed_unit.setFont(QFont("Arial", 16))
        speed_unit.setStyleSheet("color: #888888;")
        speed_layout.addWidget(speed_unit)
        
        top_layout.addLayout(speed_layout, stretch=3)
        
        # Fahrmodus (rechts)
        self.gear_display = GearDisplay()
        top_layout.addWidget(self.gear_display, stretch=1)
        
        main_layout.addLayout(top_layout, stretch=1)
        
        # ====== Power Gauge (Mitte) ======
        self.power_gauge = PowerGauge()
        main_layout.addWidget(self.power_gauge, stretch=2)
        
        # ====== Untere Info-Zeile ======
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # Links: Range & Consumption
        left_col = QVBoxLayout()
        left_col.setSpacing(5)
        
        self.range_display = DigitalDisplay(t("range"), "km")
        self.range_display.set_color(self._get_color("cyan"))
        self.range_display.set_decimals(0)
        left_col.addWidget(self.range_display)
        
        # Verbrauch: Zwei Displays nebeneinander
        consumption_layout = QHBoxLayout()
        consumption_layout.setSpacing(5)
        
        self.consumption_now_display = DigitalDisplay(t("consumption_now"), "kWh/100km")
        self.consumption_now_display.set_color(self._get_color("yellow"))
        self.consumption_now_display.set_decimals(1)
        consumption_layout.addWidget(self.consumption_now_display)
        
        self.consumption_avg_display = DigitalDisplay(t("consumption_avg"), "kWh/100km")
        self.consumption_avg_display.set_color(self._get_color("orange"))
        self.consumption_avg_display.set_decimals(1)
        consumption_layout.addWidget(self.consumption_avg_display)
        
        left_col.addLayout(consumption_layout)
        
        bottom_layout.addLayout(left_col, stretch=1)
        
        # Rechts: SOC Bar
        right_col = QVBoxLayout()
        right_col.setSpacing(5)
        
        soc_label = QLabel(t("charge_state"))
        soc_label.setFont(QFont("Arial", 14))
        soc_label.setStyleSheet("color: #aaaaaa;")
        soc_label.setAlignment(Qt.AlignCenter)
        right_col.addWidget(soc_label)
        
        self.soc_bar = BatteryBar()
        right_col.addWidget(self.soc_bar, stretch=1)
        
        # SOH klein darunter
        self.soh_label = QLabel("SOH: ---%")
        self.soh_label.setFont(QFont("Arial", 11))
        self.soh_label.setStyleSheet("color: #888888;")
        self.soh_label.setAlignment(Qt.AlignCenter)
        right_col.addWidget(self.soh_label)
        
        bottom_layout.addLayout(right_col, stretch=1)
        
        main_layout.addLayout(bottom_layout, stretch=2)
        
        self.setLayout(main_layout)
    
    def update_data(self, state: dict):
        """
        Aktualisiert Anzeige mit neuen Daten.
        
        Args:
            state: Dict mit keys: speed_kmh, power_kW, soc_pct, range_km,
                   consumption_kwh_100km, soh_pct, gear, pcu_ambient_temp_C
        """
        # Status-Bar (kompletter State für Fehlerprüfung)
        self.status_bar.set_state(state)
        ambient_temp = state.get("pcu_ambient_temp_C")
        if ambient_temp is not None:
            self.status_bar.set_ambient_temp(ambient_temp)
        
        # Geschwindigkeit
        speed = state.get("speed_kmh", 0.0)
        self.speed_label.setText(f"{speed:.0f}")
        
        # Fahrmodus
        gear = state.get("gear", "P")
        self.gear_display.set_gear(gear)
        
        # Power Gauge
        power = state.get("power_kW", 0.0)
        self.power_gauge.set_power(power)
        
        # Reichweite
        range_km = state.get("range_km", 0.0)
        self.range_display.set_value(range_km)
        
        # Verbrauch aktuell
        consumption_now = state.get("consumption_kwh_100km", 0.0)
        self.consumption_now_display.set_value(consumption_now)
        
        # Verbrauch Durchschnitt (Trip)
        consumption_avg = state.get("consumption_trip_kwh_100km", 0.0)
        self.consumption_avg_display.set_value(consumption_avg)
        
        # SOC
        soc = state.get("soc_pct", 0.0)
        self.soc_bar.set_soc(soc)
        
        # SOH
        soh = state.get("soh_pct")
        if soh is not None:
            self.soh_label.setText(f"SOH: {soh:.0f}%")
        else:
            self.soh_label.setText("SOH: ---")
    
    def _get_color(self, name: str):
        """Helper für Farben."""
        from PyQt5.QtGui import QColor
        colors = {
            "cyan": QColor(0, 255, 200),
            "yellow": QColor(255, 220, 0),
            "green": QColor(0, 255, 100),
            "red": QColor(255, 100, 100),
            "orange": QColor(255, 140, 0),
        }
        return colors.get(name, QColor(255, 255, 255))


# Test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    screen = MainScreen()
    screen.setWindowTitle("Main Screen Test")
    screen.resize(800, 480)
    screen.setStyleSheet("background-color: #1a1a1a;")
    
    # Test-Daten
    test_data = {
        "speed_kmh": 72.5,
        "power_kW": -8.2,
        "soc_pct": 68.0,
        "range_km": 95.0,
        "consumption_kwh_100km": 16.3,
        "soh_pct": 92.5
    }
    screen.update_data(test_data)
    
    screen.show()
    sys.exit(app.exec_())
