# charge_screen.py
# Lade-Ansicht: Ladestatus, Ladezeit, Ladeleistung

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from widgets import DigitalDisplay, BatteryBar, StatusBar
from datetime import datetime, timedelta


class ChargeScreen(QWidget):
    """
    Lade-Bildschirm.
    
    Zeigt:
    - Ladestatus (AC/DC, Leistung)
    - Geschätzte Zeit bis voll
    - Ladekurve (SOC-Fortschritt)
    - Mains-Spannung & Strom
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.charge_start_time = None
        self.charge_start_soc = None
        self._init_ui()
    
    def _init_ui(self):
        """Erstellt UI-Layout."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # ====== Status-Bar ======
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # ====== Titel ======
        title = QLabel("LADEN")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #00ff66;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # ====== SOC-Balken ======
        self.soc_bar = BatteryBar()
        main_layout.addWidget(self.soc_bar)
        
        # ====== Status-Text ======
        self.status_label = QLabel("Nicht verbunden")
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setStyleSheet("color: #888888;")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # ====== Werte-Grid ======
        grid = QHBoxLayout()
        grid.setSpacing(10)
        
        # AC Spannung
        self.mains_voltage_display = DigitalDisplay("AC Spannung", "V")
        self.mains_voltage_display.set_decimals(0)
        self.mains_voltage_display.set_color(QColor(255, 200, 0))
        grid.addWidget(self.mains_voltage_display)
        
        # AC Strom
        self.mains_current_display = DigitalDisplay("AC Strom", "A")
        self.mains_current_display.set_decimals(1)
        self.mains_current_display.set_color(QColor(0, 200, 255))
        grid.addWidget(self.mains_current_display)
        
        # DC Leistung (aus Batterie-Sicht: + beim Laden, - beim Entladen)
        self.charge_power_display = DigitalDisplay("Leistung", "kW")
        self.charge_power_display.set_decimals(2)
        self.charge_power_display.set_color(QColor(0, 255, 100))
        grid.addWidget(self.charge_power_display)
        
        main_layout.addLayout(grid)
        
        # ====== Zeit-Schätzungen ======
        time_layout = QVBoxLayout()
        
        # Verstrichene Zeit
        self.elapsed_label = QLabel("Ladezeit: --:--")
        self.elapsed_label.setFont(QFont("Arial", 14))
        self.elapsed_label.setStyleSheet("color: #aaaaaa;")
        self.elapsed_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.elapsed_label)
        
        # Verbleibende Zeit
        self.remaining_label = QLabel("Verbleibend: --:--")
        self.remaining_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.remaining_label.setStyleSheet("color: #00ffcc;")
        self.remaining_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.remaining_label)
        
        # Fertig um...
        self.complete_label = QLabel("Fertig: --:--")
        self.complete_label.setFont(QFont("Arial", 12))
        self.complete_label.setStyleSheet("color: #888888;")
        self.complete_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.complete_label)
        
        main_layout.addLayout(time_layout)
        
        # ====== Zusatz-Infos ======
        info_layout = QHBoxLayout()
        
        # Max verfügbarer AC-Strom
        self.max_ac_label = QLabel("Max AC: --- A")
        self.max_ac_label.setFont(QFont("Arial", 12))
        self.max_ac_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(self.max_ac_label)
        
        # Geladene Energie
        self.energy_label = QLabel("Geladen: --- kWh")
        self.energy_label.setFont(QFont("Arial", 12))
        self.energy_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(self.energy_label)
        
        main_layout.addLayout(info_layout)
        
        self.setLayout(main_layout)
    
    def update_data(self, state: dict):
        """
        Aktualisiert Anzeige mit neuen Daten.
        
        Args:
            state: Dict mit Lade-Daten
        """
        # Status-Bar (kompletter State für Fehlerprüfung)
        self.status_bar.set_state(state)
        ambient_temp = state.get("pcu_ambient_temp_C")
        if ambient_temp is not None:
            self.status_bar.set_ambient_temp(ambient_temp)
        
        # SOC
        soc = state.get("soc_pct", 0.0)
        self.soc_bar.set_soc(soc)
        
        # Mains (AC)
        mains_v = state.get("mains_voltage_V", 0.0)
        mains_a = state.get("mains_current_A", 0.0)
        self.mains_voltage_display.set_value(mains_v)
        self.mains_current_display.set_value(mains_a)
        
        # DC Power (aus Batterie-Sicht: + beim Laden, - beim Entladen)
        # power_kW ist normalerweise positiv beim Entladen, negativ beim Laden
        # Wir drehen das Vorzeichen um für Batterie-Perspektive
        power_kw = -state.get("power_kW", 0.0)  # Negativ = Batterie-Sicht
        self.charge_power_display.set_value(power_kw)
        
        # Max AC Current
        max_ac = state.get("max_available_AC_A", 0.0)
        self.max_ac_label.setText(f"Max AC: {max_ac:.1f} A")
        
        # Status-Erkennung
        is_charging = state.get("vehicle_charge_enabled", False) and mains_v > 100
        
        if is_charging:
            self.status_label.setText("⚡ LADEN")
            self.status_label.setStyleSheet("color: #00ff66;")
            
            # Lade-Start tracken
            if self.charge_start_time is None:
                self.charge_start_time = datetime.now()
                self.charge_start_soc = soc
            
            # Zeit-Berechnungen (power_kw ist positiv beim Laden)
            self._update_time_estimates(soc, abs(power_kw))
        
        else:
            self.status_label.setText("Nicht verbunden")
            self.status_label.setStyleSheet("color: #888888;")
            
            # Reset
            self.charge_start_time = None
            self.charge_start_soc = None
            self.elapsed_label.setText("Ladezeit: --:--")
            self.remaining_label.setText("Verbleibend: --:--")
            self.complete_label.setText("Fertig: --:--")
            self.energy_label.setText("Geladen: --- kWh")
    
    def _update_time_estimates(self, current_soc: float, power_kw: float):
        """Berechnet Zeit-Schätzungen während des Ladens."""
        if self.charge_start_time is None or self.charge_start_soc is None:
            return
        
        # Verstrichene Zeit
        elapsed = datetime.now() - self.charge_start_time
        elapsed_str = str(elapsed).split('.')[0]  # HH:MM:SS
        self.elapsed_label.setText(f"Ladezeit: {elapsed_str}")
        
        # Geladene SOC-Prozent
        charged_soc = current_soc - self.charge_start_soc
        
        if charged_soc > 0.5:  # Mindestens 0.5% geladen
            # Verbleibende SOC bis 100%
            remaining_soc = 100.0 - current_soc
            
            # Lade-Rate (% pro Sekunde)
            rate_pct_per_sec = charged_soc / elapsed.total_seconds()
            
            if rate_pct_per_sec > 0:
                # Geschätzte verbleibende Sekunden
                remaining_sec = remaining_soc / rate_pct_per_sec
                remaining_td = timedelta(seconds=int(remaining_sec))
                
                # Format HH:MM
                hours = remaining_td.seconds // 3600
                minutes = (remaining_td.seconds % 3600) // 60
                self.remaining_label.setText(f"Verbleibend: {hours:02d}:{minutes:02d}")
                
                # Fertig-Zeitpunkt
                complete_time = datetime.now() + remaining_td
                self.complete_label.setText(f"Fertig: {complete_time.strftime('%H:%M')}")
            else:
                self.remaining_label.setText("Verbleibend: Berechne...")
        
        else:
            self.remaining_label.setText("Verbleibend: Sammle Daten...")
        
        # Geladene Energie (Schätzung: 24 kWh * SOC-Differenz)
        battery_capacity_kwh = 24.0
        energy_charged_kwh = (charged_soc / 100.0) * battery_capacity_kwh
        self.energy_label.setText(f"Geladen: {energy_charged_kwh:.2f} kWh")


# Test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    screen = ChargeScreen()
    screen.setWindowTitle("Charge Screen Test")
    screen.resize(800, 480)
    screen.setStyleSheet("background-color: #1a1a1a;")
    
    # Simuliere Laden
    test_data = {
        "soc_pct": 68.5,
        "mains_voltage_V": 230.0,
        "mains_current_A": 12.8,
        "power_kW": 2.95,
        "max_available_AC_A": 16.0,
        "vehicle_charge_enabled": True,
    }
    
    screen.update_data(test_data)
    
    # Simuliere Fortschritt mit Timer
    def simulate_charging():
        test_data["soc_pct"] += 0.1
        if test_data["soc_pct"] > 100:
            test_data["soc_pct"] = 68.5
            screen.charge_start_time = None
        screen.update_data(test_data)
    
    timer = QTimer()
    timer.timeout.connect(simulate_charging)
    timer.start(2000)  # Alle 2 Sekunden
    
    screen.show()
    sys.exit(app.exec_())
