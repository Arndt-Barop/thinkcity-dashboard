# battery_screen.py
# Batterie-Detailansicht: Zellspannungen, Temperaturen, Limits

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from widgets import DigitalDisplay, StatusBar
from translations import get_translator


class BatteryScreen(QWidget):
    """
    Batterie-Detail-Bildschirm.
    
    Zeigt:
    - Spannungs-/Strom-Details
    - Zellspannungen (Min/Max/Avg/Delta)
    - Temperaturen (Pack/Ambient)
    - Limits & Status-Flags
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
        
        # ====== Status-Bar ======
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # ====== Titel ======
        title = QLabel(t("battery_details"))
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ffcc;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # ====== Haupt-Werte Grid ======
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Zeile 1: Voltage & Current
        self.voltage_display = DigitalDisplay(t("voltage"), "V")
        self.voltage_display.set_decimals(1)
        grid.addWidget(self.voltage_display, 0, 0)
        
        self.current_display = DigitalDisplay(t("current"), "A")
        self.current_display.set_decimals(1)
        grid.addWidget(self.current_display, 0, 1)
        
        self.power_display = DigitalDisplay(t("power"), "kW")
        self.power_display.set_decimals(2)
        grid.addWidget(self.power_display, 0, 2)
        
        # Zeile 2: Temperaturen
        self.pack_temp_display = DigitalDisplay(t("pack_temp"), "°C")
        self.pack_temp_display.set_decimals(1)
        self.pack_temp_display.set_color(QColor(255, 140, 0))
        grid.addWidget(self.pack_temp_display, 1, 0)
        
        self.ambient_temp_display = DigitalDisplay(t("ambient_temp"), "°C")
        self.ambient_temp_display.set_decimals(1)
        self.ambient_temp_display.set_color(QColor(150, 150, 255))
        grid.addWidget(self.ambient_temp_display, 1, 1)
        
        self.dod_display = DigitalDisplay("DoD", "%")
        self.dod_display.set_decimals(1)
        self.dod_display.set_color(QColor(255, 100, 100))
        grid.addWidget(self.dod_display, 1, 2)
        
        main_layout.addLayout(grid)
        
        # ====== Zellspannungen (nur bei EnerDel) ======
        cell_group = QVBoxLayout()
        
        cell_title = QLabel(t("cell_voltages_enerdel"))
        cell_title.setFont(QFont("Arial", 14, QFont.Bold))
        cell_title.setStyleSheet("color: #aaaaaa;")
        cell_group.addWidget(cell_title)
        
        cell_grid = QGridLayout()
        cell_grid.setSpacing(8)
        
        # Min Cell
        self.cell_min_label = QLabel(t("min") + ":")
        self.cell_min_label.setFont(QFont("Arial", 12))
        self.cell_min_label.setStyleSheet("color: #888888;")
        cell_grid.addWidget(self.cell_min_label, 0, 0)
        
        self.cell_min_value = QLabel("--- V")
        self.cell_min_value.setFont(QFont("Arial", 14, QFont.Bold))
        self.cell_min_value.setStyleSheet("color: #ff6666;")
        cell_grid.addWidget(self.cell_min_value, 0, 1)
        
        # Max Cell
        self.cell_max_label = QLabel(t("max") + ":")
        self.cell_max_label.setFont(QFont("Arial", 12))
        self.cell_max_label.setStyleSheet("color: #888888;")
        cell_grid.addWidget(self.cell_max_label, 1, 0)
        
        self.cell_max_value = QLabel("--- V")
        self.cell_max_value.setFont(QFont("Arial", 14, QFont.Bold))
        self.cell_max_value.setStyleSheet("color: #66ff66;")
        cell_grid.addWidget(self.cell_max_value, 1, 1)
        
        # Avg Cell
        self.cell_avg_label = QLabel(t("avg") + ":")
        self.cell_avg_label.setFont(QFont("Arial", 12))
        self.cell_avg_label.setStyleSheet("color: #888888;")
        cell_grid.addWidget(self.cell_avg_label, 0, 2)
        
        self.cell_avg_value = QLabel("--- V")
        self.cell_avg_value.setFont(QFont("Arial", 14, QFont.Bold))
        self.cell_avg_value.setStyleSheet("color: #ffcc00;")
        cell_grid.addWidget(self.cell_avg_value, 0, 3)
        
        # Delta Cell
        self.cell_delta_label = QLabel(t("delta") + ":")
        self.cell_delta_label.setFont(QFont("Arial", 12))
        self.cell_delta_label.setStyleSheet("color: #888888;")
        cell_grid.addWidget(self.cell_delta_label, 1, 2)
        
        self.cell_delta_value = QLabel("--- V")
        self.cell_delta_value.setFont(QFont("Arial", 14, QFont.Bold))
        self.cell_delta_value.setStyleSheet("color: #ff9900;")
        cell_grid.addWidget(self.cell_delta_value, 1, 3)
        
        cell_group.addLayout(cell_grid)
        main_layout.addLayout(cell_group)
        
        # ====== Status-Flags ======
        status_group = QVBoxLayout()
        
        status_title = QLabel(t("status"))
        status_title.setFont(QFont("Arial", 14, QFont.Bold))
        status_title.setStyleSheet("color: #aaaaaa;")
        status_group.addWidget(status_title)
        
        # Grid for flags
        flags_grid = QGridLayout()
        flags_grid.setSpacing(5)
        
        self.flag_labels = {}
        flags = [
            ("charge_en", t("charge_enabled")),
            ("discharge_en", t("discharge_enabled")),
            ("regen_en", t("regen_enabled")),
            ("dc_dc_en", t("dc_dc_enabled")),
            ("iso_error", t("iso_error")),
            ("emergency", t("emergency")),
        ]
        
        for idx, (key, text) in enumerate(flags):
            row = idx // 2
            col = idx % 2
            
            label = QLabel(f"⚫ {text}")
            label.setFont(QFont("Arial", 11))
            label.setStyleSheet("color: #666666;")
            flags_grid.addWidget(label, row, col)
            
            self.flag_labels[key] = label
        
        status_group.addLayout(flags_grid)
        main_layout.addLayout(status_group)
        
        # ====== Batterie-Typ ======
        self.battery_type_label = QLabel(t("type") + ": ---")
        self.battery_type_label.setFont(QFont("Arial", 12))
        self.battery_type_label.setStyleSheet("color: #888888;")
        self.battery_type_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.battery_type_label)
        
        self.setLayout(main_layout)
    
    def update_data(self, state: dict):
        """
        Aktualisiert Anzeige mit neuen Daten.
        
        Args:
            state: Dict mit allen Batterie-Werten
        """
        # Status bar (complete state for error checking)
        self.status_bar.set_state(state)
        ambient_temp = state.get("pcu_ambient_temp_C")
        if ambient_temp is not None:
            self.status_bar.set_ambient_temp(ambient_temp)
        
        # Haupt-Werte
        self.voltage_display.set_value(state.get("voltage_V", 0.0))
        self.current_display.set_value(state.get("current_A", 0.0))
        self.power_display.set_value(state.get("power_kW", 0.0))
        
        # Temperaturen
        self.pack_temp_display.set_value(state.get("pack_temp_C", 0.0))
        self.ambient_temp_display.set_value(state.get("pcu_ambient_temp_C", 0.0))
        self.dod_display.set_value(state.get("dod_pct", 0.0))
        
        # Cell voltages (EnerDel)
        if state.get("is_enerdel"):
            min_v = state.get("e_pack_min_cell_V")
            max_v = state.get("e_pack_max_cell_V")
            avg_v = state.get("e_pack_avg_cell_V")
            delta_v = state.get("e_pack_delta_cell_V")
            
            if min_v is not None:
                self.cell_min_value.setText(f"{min_v:.3f} V")
            if max_v is not None:
                self.cell_max_value.setText(f"{max_v:.3f} V")
            if avg_v is not None:
                self.cell_avg_value.setText(f"{avg_v:.3f} V")
            if delta_v is not None:
                self.cell_delta_value.setText(f"{delta_v:.3f} V")
                
                # Delta color: Green at <50mV, Red at >100mV
                if delta_v < 0.05:
                    color = "#66ff66"
                elif delta_v < 0.1:
                    color = "#ffcc00"
                else:
                    color = "#ff6666"
                self.cell_delta_value.setStyleSheet(f"color: {color};")
        
        # Status-Flags
        flags_map = {
            "charge_en": state.get("vehicle_charge_enabled"),
            "discharge_en": state.get("discharge_enabled"),
            "regen_en": state.get("regen_brake_enabled"),
            "dc_dc_en": state.get("dc_dc_enabled"),
            "iso_error": state.get("iso_error"),
            "emergency": state.get("emergency"),
        }
        
        for key, value in flags_map.items():
            if key in self.flag_labels:
                label = self.flag_labels[key]
                text = label.text().split(" ", 1)[1]  # Nur Text ohne Symbol
                
                # Fehler-Flags (iso_error, emergency) -> Rot wenn aktiv
                # Normal flags (charge_en, discharge_en, etc.) -> Green when active
                is_error_flag = key in ["iso_error", "emergency"]
                
                if value is True:
                    if is_error_flag:
                        # Fehler aktiv = ROT (Alarm!)
                        label.setText(f"🔴 {text}")
                        label.setStyleSheet("color: #ff4444;")
                    else:
                        # Normal active = GREEN (OK)
                        label.setText(f"🟢 {text}")
                        label.setStyleSheet("color: #66ff66;")
                else:
                    # False oder None: inaktiv/unbekannt = grau (neutral)
                    label.setText(f"⚫ {text}")
                    label.setStyleSheet("color: #888888;")
        
        # Batterie-Typ
        is_enerdel = state.get("is_enerdel", False)
        t = self.translator.get
        batt_type = "EnerDel Li-Ion" if is_enerdel else "Zebra Na-NiCl2"
        self.battery_type_label.setText(f"{t('type')}: {batt_type}")


# Test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    screen = BatteryScreen()
    screen.setWindowTitle("Battery Screen Test")
    screen.resize(800, 480)
    screen.setStyleSheet("background-color: #1a1a1a;")
    
    # Test-Daten (EnerDel)
    test_data = {
        "voltage_V": 332.5,
        "current_A": -18.2,
        "power_kW": -6.05,
        "pack_temp_C": 26.5,
        "pcu_ambient_temp_C": 22.0,
        "dod_pct": 32.0,
        "is_enerdel": True,
        "e_pack_min_cell_V": 3.452,
        "e_pack_max_cell_V": 3.498,
        "e_pack_avg_cell_V": 3.473,
        "e_pack_delta_cell_V": 0.046,
        "vehicle_charge_enabled": True,
        "discharge_enabled": True,
        "regen_brake_enabled": True,
        "dc_dc_enabled": True,
        "iso_error": False,
        "emergency": False,
    }
    screen.update_data(test_data)
    
    screen.show()
    sys.exit(app.exec_())
