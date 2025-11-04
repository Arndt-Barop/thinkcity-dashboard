# cell_voltages_screen.py
# Detaillierte Zellspannungs-Ansicht mit Bargraphen

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from widgets import StatusBar


class CellVoltageBar(QWidget):
    """Ein einzelner vertikaler Bargraph für eine Zellspannung."""
    
    def __init__(self, cell_num, parent=None):
        super().__init__(parent)
        self.cell_num = cell_num
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Wert-Label (oben)
        self.value_label = QLabel("---")
        self.value_label.setFont(QFont("Arial", 8))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.value_label)
        
        # Vertikaler Progressbar (kleiner)
        self.bar = QProgressBar()
        self.bar.setOrientation(Qt.Vertical)
        self.bar.setMinimum(0)
        self.bar.setMaximum(1000)  # 0.0 - 10.0V als 0-1000
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedSize(25, 90)  # Kleiner: 25x90 statt 35x120
        # Initialer Style (wird dynamisch überschrieben)
        self.bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444444;
                border-radius: 3px;
                background-color: #111111;
            }
            QProgressBar::chunk {
                background-color: #333333;
            }
        """)
        layout.addWidget(self.bar, alignment=Qt.AlignCenter)
        
        # Zell-Nummer (unten)
        self.num_label = QLabel(f"Z{self.cell_num}")
        self.num_label.setFont(QFont("Arial", 7))
        self.num_label.setAlignment(Qt.AlignCenter)
        self.num_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.num_label)
        
        self.setLayout(layout)
    
    def set_voltage(self, voltage_v):
        """Setzt Spannung in Volt (z.B. 3.65)."""
        if voltage_v is None or voltage_v <= 0:
            self.value_label.setText("---")
            self.bar.setValue(0)
            self.value_label.setStyleSheet("color: #666666;")
            self.bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #444444;
                    border-radius: 3px;
                    background-color: #111111;
                }
                QProgressBar::chunk {
                    background-color: #333333;
                }
            """)
        else:
            self.value_label.setText(f"{voltage_v:.3f}")
            # Skala: 0-10V → 0-1000
            bar_value = int(voltage_v * 100)
            self.bar.setValue(bar_value)
            
            # Farbe je nach Spannung
            # KRITISCH: Zu hoch (> 4.2V) = ROT (gefährlich!)
            # WARNUNG: Zu niedrig (< 3.0V) = ORANGE
            # OK: Normal (3.5-4.1V) = GRÜN
            # GRENZWERTIG: Dazwischen = GELB
            
            if voltage_v > 4.2:
                color = "#ff0000"  # Rot (KRITISCH zu hoch!)
                border_color = "#ff0000"  # Rote Umrandung!
                border_width = "3px"
            elif voltage_v < 3.0:
                color = "#ff8800"  # Orange (zu niedrig)
                border_color = "#ff8800"  # Orange Umrandung
                border_width = "3px"
            elif 3.5 <= voltage_v <= 4.1:
                color = "#00ff00"  # Grün (optimal)
                border_color = "#444444"  # Normale Umrandung
                border_width = "2px"
            else:
                color = "#ffff00"  # Gelb (grenzwertig)
                border_color = "#888888"  # Hellere Umrandung
                border_width = "2px"
            
            # Setze Label-Farbe
            self.value_label.setStyleSheet(f"color: {color};")
            
            # Setze Bar-Style mit einheitlicher Farbe (KEIN Verlauf!)
            self.bar.setStyleSheet(f"""
                QProgressBar {{
                    border: {border_width} solid {border_color};
                    border-radius: 3px;
                    background-color: #111111;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """)


class CellVoltagesScreen(QWidget):
    """
    Detaillierte Zellspannungs-Ansicht.
    
    Zeigt alle einzelnen Zellspannungen als vertikale Bargraphen.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cell_bars = {}
        self._init_ui()
    
    def _init_ui(self):
        """Erstellt UI-Layout."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # ====== Status-Bar ======
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # ====== Titel ======
        title = QLabel("ZELLSPANNUNGEN")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ffcc;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Info-Zeile
        info_layout = QHBoxLayout()
        
        self.min_cell_label = QLabel("Min: --- V (Z--)")
        self.min_cell_label.setFont(QFont("Arial", 11))
        self.min_cell_label.setStyleSheet("color: #ff6666;")
        info_layout.addWidget(self.min_cell_label)
        
        info_layout.addStretch()
        
        self.avg_cell_label = QLabel("Ø: --- V")
        self.avg_cell_label.setFont(QFont("Arial", 11))
        self.avg_cell_label.setStyleSheet("color: #00ff00;")
        info_layout.addWidget(self.avg_cell_label)
        
        info_layout.addStretch()
        
        self.max_cell_label = QLabel("Max: --- V (Z--)")
        self.max_cell_label.setFont(QFont("Arial", 11))
        self.max_cell_label.setStyleSheet("color: #66ff66;")
        info_layout.addWidget(self.max_cell_label)
        
        info_layout.addStretch()
        
        self.delta_label = QLabel("Δ: --- mV")
        self.delta_label.setFont(QFont("Arial", 11))
        self.delta_label.setStyleSheet("color: #ffff00;")
        info_layout.addWidget(self.delta_label)
        
        main_layout.addLayout(info_layout)
        
        # ====== Container für Zellen (KEINE Scroll-Area) ======
        # 88 Zellen auf 4 Reihen = 22 Zellen pro Reihe
        
        # Container für alle 4 Reihen
        rows_layout = QVBoxLayout()
        rows_layout.setSpacing(3)
        
        self.row_layouts = []
        
        for row_num in range(4):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(2)
            row_layout.setContentsMargins(0, 0, 0, 0)
            self.row_layouts.append(row_layout)
            
            row_container = QWidget()
            row_container.setLayout(row_layout)
            rows_layout.addWidget(row_container)
        
        # EnerDel hat 88 Zellen (11 Module × 8 Zellen)
        # Verteile auf 4 Reihen: 22 + 22 + 22 + 22
        for i in range(1, 89):  # Zellen 1-88
            bar = CellVoltageBar(i)
            self.cell_bars[i] = bar
            
            # Reihen-Index bestimmen (0-3)
            row_idx = (i - 1) // 22
            self.row_layouts[row_idx].addWidget(bar)
        
        main_layout.addLayout(rows_layout)
        
        # Hinweis-Text
        hint = QLabel("💡 Grün = optimal (3.5-4.1V) | Gelb = grenzwertig | 🔴 Rot = KRITISCH zu hoch! | 🟠 Orange = zu niedrig")
        hint.setFont(QFont("Arial", 9))
        hint.setStyleSheet("color: #888888;")
        hint.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(hint)
        
        self.setLayout(main_layout)
    
    def update(self, state):
        """Aktualisiert Anzeige mit neuem State."""
        # Status-Bar (kompletter State für Fehlerprüfung)
        self.status_bar.set_state(state)
        ambient_temp = state.get("pcu_ambient_temp_C")
        if ambient_temp is not None:
            self.status_bar.set_ambient_temp(ambient_temp)
        
        cell_voltages = state.get("cell_voltages", [])
        
        if not cell_voltages or len(cell_voltages) == 0:
            # Keine Daten
            for bar in self.cell_bars.values():
                bar.set_voltage(None)
            self.min_cell_label.setText("Min: --- V (Z--)")
            self.max_cell_label.setText("Max: --- V (Z--)")
            self.avg_cell_label.setText("Ø: --- V")
            self.delta_label.setText("Δ: --- mV")
            return
        
        # Update Bargraphen
        for i, voltage in enumerate(cell_voltages, start=1):
            if i in self.cell_bars:
                self.cell_bars[i].set_voltage(voltage)
        
        # Statistiken
        valid_voltages = [v for v in cell_voltages if v is not None and v > 0]
        
        if valid_voltages:
            min_v = min(valid_voltages)
            max_v = max(valid_voltages)
            avg_v = sum(valid_voltages) / len(valid_voltages)
            delta_mv = (max_v - min_v) * 1000
            
            min_idx = cell_voltages.index(min_v) + 1
            max_idx = cell_voltages.index(max_v) + 1
            
            self.min_cell_label.setText(f"Min: {min_v:.3f} V (Z{min_idx})")
            self.max_cell_label.setText(f"Max: {max_v:.3f} V (Z{max_idx})")
            self.avg_cell_label.setText(f"Ø: {avg_v:.3f} V")
            self.delta_label.setText(f"Δ: {delta_mv:.1f} mV")
            
            # Delta-Farbe (grün < 50mV, gelb < 100mV, rot >= 100mV)
            if delta_mv < 50:
                delta_color = "#00ff00"
            elif delta_mv < 100:
                delta_color = "#ffff00"
            else:
                delta_color = "#ff4444"
            
            self.delta_label.setStyleSheet(f"color: {delta_color};")
        else:
            self.min_cell_label.setText("Min: --- V (Z--)")
            self.max_cell_label.setText("Max: --- V (Z--)")
            self.avg_cell_label.setText("Ø: --- V")
            self.delta_label.setText("Δ: --- mV")


# Test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    screen = CellVoltagesScreen()
    screen.setStyleSheet("background-color: #000000; color: #ffffff;")
    screen.resize(1280, 800)
    
    # Test-Daten
    import random
    test_voltages = [3.6 + random.uniform(-0.1, 0.1) for _ in range(88)]
    screen.update({"cell_voltages": test_voltages})
    
    screen.show()
    sys.exit(app.exec_())
