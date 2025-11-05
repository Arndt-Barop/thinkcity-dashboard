# settings_screen.py
# Settings-Screen für grundlegende Konfiguration

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QCheckBox, QLineEdit,
                             QComboBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import json
import os

class SettingsScreen(QWidget):
    """
    Settings-Screen für:
    - CAN-Interface Auswahl (can0 / vcan0)
    - WLAN-Konfiguration
    - NAS Sync-Einstellungen
    - Datenbank-Pfad
    - Debug-Optionen
    """
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_file = os.path.expanduser("~/thinkcity-dashboard-v3/config.json")
        self.settings = self.load_settings()
        self.init_ui()
        
    def load_settings(self):
        """Lade Settings aus JSON-Datei."""
        defaults = {
            "can_interface": "can0",
            "simulation_mode": False,
            "nas_sync_enabled": False,
            "nas_host": "",
            "nas_path": "/backup/thinkcity",
            "nas_user": "",
            "wifi_ssid": "",
            "sync_on_wifi_only": True,
            "db_path": "/home/pi/thinkcity-dashboard-v3/thinkcity.db",
            # Logging Settings
            "logging_enabled": True,
            "logging_interval_sec": 1,
            "logging_fields": [
                "speed_kmh", "soc_pct", "voltage_V", "current_A", "power_kW",
                "pack_temp_C", "ambient_temp_C", "consumption_wh_km", "range_km",
                "odo_km", "latitude", "longitude"
            ]
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except Exception as e:
                print(f"Settings load error: {e}")
        
        return defaults
    
    def save_settings(self):
        """Speichere Settings in JSON-Datei."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to {self.config_file}")
            self.settings_changed.emit(self.settings)
        except Exception as e:
            print(f"Settings save error: {e}")
    
    def init_ui(self):
        """Erstelle UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Titel
        title = QLabel("⚙️ Einstellungen")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Scroll-Bereich für Settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # === CAN-Interface ===
        can_group = self.create_can_group()
        scroll_layout.addWidget(can_group)
        
        # === WLAN ===
        wifi_group = self.create_wifi_group()
        scroll_layout.addWidget(wifi_group)
        
        # === NAS Sync ===
        nas_group = self.create_nas_group()
        scroll_layout.addWidget(nas_group)
        
        # === Datenbank ===
        db_group = self.create_db_group()
        scroll_layout.addWidget(db_group)
        
        # === Logging ===
        logging_group = self.create_logging_group()
        scroll_layout.addWidget(logging_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setFont(QFont("Arial", 16))
        save_btn.setMinimumHeight(60)
        save_btn.clicked.connect(self.on_save)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #27ae60;
            }
        """)
        
        cancel_btn = QPushButton("❌ Abbrechen")
        cancel_btn.setFont(QFont("Arial", 16))
        cancel_btn.setMinimumHeight(60)
        cancel_btn.clicked.connect(self.on_cancel)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)
        
        # System-Buttons (Shutdown/Reboot)
        system_layout = QHBoxLayout()
        system_layout.setSpacing(10)
        
        reboot_btn = QPushButton("🔄 Neustart")
        reboot_btn.setFont(QFont("Arial", 14))
        reboot_btn.setMinimumHeight(50)
        reboot_btn.clicked.connect(self.on_reboot)
        reboot_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #e67e22;
            }
        """)
        
        shutdown_btn = QPushButton("⏻ Herunterfahren")
        shutdown_btn.setFont(QFont("Arial", 14))
        shutdown_btn.setMinimumHeight(50)
        shutdown_btn.clicked.connect(self.on_shutdown)
        shutdown_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        
        system_layout.addWidget(reboot_btn)
        system_layout.addWidget(shutdown_btn)
        main_layout.addLayout(system_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #2c3e50;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QComboBox {
                background-color: #2c3e50;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
    
    def create_can_group(self):
        """CAN-Interface Settings."""
        group = QGroupBox("🔌 CAN-Interface")
        layout = QVBoxLayout()
        
        # Interface Auswahl
        interface_layout = QHBoxLayout()
        interface_layout.addWidget(QLabel("Interface:"))
        
        self.can_combo = QComboBox()
        self.can_combo.addItems(["can0", "vcan0"])
        self.can_combo.setCurrentText(self.settings["can_interface"])
        interface_layout.addWidget(self.can_combo)
        layout.addLayout(interface_layout)
        
        # Simulation Mode
        self.sim_checkbox = QCheckBox("Simulation beim Boot starten (nur vcan0)")
        self.sim_checkbox.setChecked(self.settings["simulation_mode"])
        layout.addWidget(self.sim_checkbox)
        
        group.setLayout(layout)
        return group
    
    def create_wifi_group(self):
        """WLAN Settings."""
        group = QGroupBox("📶 WLAN")
        layout = QVBoxLayout()
        
        # Home SSID
        ssid_layout = QHBoxLayout()
        ssid_layout.addWidget(QLabel("Heim-WLAN SSID:"))
        self.wifi_ssid = QLineEdit(self.settings["wifi_ssid"])
        self.wifi_ssid.setPlaceholderText("z.B. MeinWLAN")
        ssid_layout.addWidget(self.wifi_ssid)
        layout.addLayout(ssid_layout)
        
        # Sync only on WLAN
        self.wifi_only_checkbox = QCheckBox("Sync nur bei WLAN-Verbindung")
        self.wifi_only_checkbox.setChecked(self.settings["sync_on_wifi_only"])
        layout.addWidget(self.wifi_only_checkbox)
        
        info = QLabel("ℹ️ Sync erfolgt nur wenn mit diesem WLAN verbunden")
        info.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def create_nas_group(self):
        """NAS Sync Settings."""
        group = QGroupBox("💾 NAS Synchronisation")
        layout = QVBoxLayout()
        
        # Enable Sync
        self.nas_enable = QCheckBox("NAS-Sync aktivieren")
        self.nas_enable.setChecked(self.settings["nas_sync_enabled"])
        layout.addWidget(self.nas_enable)
        
        # NAS Host
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("NAS Host/IP:"))
        self.nas_host = QLineEdit(self.settings["nas_host"])
        self.nas_host.setPlaceholderText("z.B. 192.168.1.100 oder nas.local")
        host_layout.addWidget(self.nas_host)
        layout.addLayout(host_layout)
        
        # NAS Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("NAS Pfad:"))
        self.nas_path = QLineEdit(self.settings["nas_path"])
        self.nas_path.setPlaceholderText("/backup/thinkcity")
        path_layout.addWidget(self.nas_path)
        layout.addLayout(path_layout)
        
        # NAS User
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Benutzer:"))
        self.nas_user = QLineEdit(self.settings["nas_user"])
        self.nas_user.setPlaceholderText("NAS Benutzername")
        user_layout.addWidget(self.nas_user)
        layout.addLayout(user_layout)
        
        info = QLabel("ℹ️ Datenbank wird nach jeder Fahrt automatisch synchronisiert")
        info.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def create_db_group(self):
        """Datenbank Settings."""
        group = QGroupBox("🗄️ Datenbank")
        layout = QVBoxLayout()
        
        # DB Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Pfad:"))
        self.db_path = QLineEdit(self.settings["db_path"])
        path_layout.addWidget(self.db_path)
        layout.addLayout(path_layout)
        
        info = QLabel("ℹ️ Standard: /home/pi/thinkcity-dashboard-v3/thinkcity.db")
        info.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def create_logging_group(self):
        """Logging Settings."""
        from PyQt5.QtWidgets import QSlider, QGridLayout
        
        group = QGroupBox("📊 Daten-Logging")
        layout = QVBoxLayout()
        
        # Logging aktivieren
        self.logging_enabled = QCheckBox("Logging aktiviert")
        self.logging_enabled.setChecked(self.settings["logging_enabled"])
        self.logging_enabled.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.logging_enabled)
        
        # Intervall-Slider
        interval_layout = QVBoxLayout()
        interval_label = QLabel(f"Log-Intervall: {self.settings['logging_interval_sec']} Sekunden")
        interval_label.setStyleSheet("font-size: 14px;")
        interval_layout.addWidget(interval_label)
        
        self.logging_interval_slider = QSlider(Qt.Horizontal)
        self.logging_interval_slider.setMinimum(1)
        self.logging_interval_slider.setMaximum(60)
        self.logging_interval_slider.setValue(self.settings["logging_interval_sec"])
        self.logging_interval_slider.setTickPosition(QSlider.TicksBelow)
        self.logging_interval_slider.setTickInterval(5)
        
        def update_interval_label(value):
            interval_label.setText(f"Log-Intervall: {value} Sekunden")
        
        self.logging_interval_slider.valueChanged.connect(update_interval_label)
        interval_layout.addWidget(self.logging_interval_slider)
        
        interval_info = QLabel("ℹ️ 1s = hohe Genauigkeit, hoher Speicher | 60s = niedrige Genauigkeit, wenig Speicher")
        interval_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        interval_info.setWordWrap(True)
        interval_layout.addWidget(interval_info)
        
        layout.addLayout(interval_layout)
        
        # Datenpunkt-Auswahl
        fields_label = QLabel("Zu loggende Datenpunkte:")
        fields_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(fields_label)
        
        # Alle verfügbaren Felder
        available_fields = {
            "speed_kmh": "🚗 Geschwindigkeit",
            "soc_pct": "🔋 Ladezustand (SOC)",
            "voltage_V": "⚡ Spannung",
            "current_A": "⚡ Strom",
            "power_kW": "⚡ Leistung",
            "pack_temp_C": "🌡️ Akku-Temperatur",
            "ambient_temp_C": "🌡️ Außentemperatur",
            "consumption_wh_km": "📊 Verbrauch Wh/km",
            "range_km": "📏 Reichweite",
            "odo_km": "🛣️ Kilometerstand",
            "latitude": "🌍 GPS Breitengrad",
            "longitude": "🌍 GPS Längengrad"
        }
        
        # Grid für Checkboxen (2 Spalten)
        fields_grid = QGridLayout()
        fields_grid.setSpacing(5)
        
        self.field_checkboxes = {}
        selected_fields = self.settings.get("logging_fields", list(available_fields.keys()))
        
        row, col = 0, 0
        for field_name, field_label in available_fields.items():
            checkbox = QCheckBox(field_label)
            checkbox.setChecked(field_name in selected_fields)
            checkbox.setStyleSheet("font-size: 12px;")
            self.field_checkboxes[field_name] = checkbox
            
            fields_grid.addWidget(checkbox, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        layout.addLayout(fields_grid)
        
        # Buttons für alle/keine
        select_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("✓ Alle")
        select_all_btn.setMaximumWidth(100)
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in self.field_checkboxes.values()])
        select_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("✗ Keine")
        select_none_btn.setMaximumWidth(100)
        select_none_btn.clicked.connect(lambda: [cb.setChecked(False) for cb in self.field_checkboxes.values()])
        select_layout.addWidget(select_none_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        group.setLayout(layout)
        return group
    
    def on_save(self):
        """Speichere Einstellungen."""
        self.settings["can_interface"] = self.can_combo.currentText()
        self.settings["simulation_mode"] = self.sim_checkbox.isChecked()
        self.settings["wifi_ssid"] = self.wifi_ssid.text()
        self.settings["sync_on_wifi_only"] = self.wifi_only_checkbox.isChecked()
        self.settings["nas_sync_enabled"] = self.nas_enable.isChecked()
        self.settings["nas_host"] = self.nas_host.text()
        self.settings["nas_path"] = self.nas_path.text()
        self.settings["nas_user"] = self.nas_user.text()
        self.settings["db_path"] = self.db_path.text()
        
        # Logging Settings
        self.settings["logging_enabled"] = self.logging_enabled.isChecked()
        self.settings["logging_interval_sec"] = self.logging_interval_slider.value()
        self.settings["logging_fields"] = [
            field_name for field_name, checkbox in self.field_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        self.save_settings()
        
        # Zeige Bestätigung
        self.show_message("✅ Einstellungen gespeichert!\n\nNeustart erforderlich für CAN-Interface Änderung.")
    
    def on_cancel(self):
        """Verwerfe Änderungen."""
        self.settings = self.load_settings()
        self.show_message("❌ Änderungen verworfen")
    
    def on_reboot(self):
        """System neu starten."""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            'Neustart bestätigen',
            'System wirklich neu starten?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.show_message("🔄 System wird neu gestartet...")
            from PyQt5.QtCore import QTimer
            import subprocess
            # Warte 2 Sekunden, dann reboot
            QTimer.singleShot(2000, lambda: subprocess.run(['sudo', 'reboot']))
    
    def on_shutdown(self):
        """System herunterfahren."""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            'Herunterfahren bestätigen',
            'System wirklich herunterfahren?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.show_message("⏻ System wird heruntergefahren...")
            from PyQt5.QtCore import QTimer
            import subprocess
            # Warte 2 Sekunden, dann shutdown
            QTimer.singleShot(2000, lambda: subprocess.run(['sudo', 'shutdown', '-h', 'now']))
    
    def show_message(self, text):
        """Zeige Nachricht (simpler Overlay)."""
        msg = QLabel(text, self)
        msg.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                font-size: 18px;
                padding: 30px;
                border-radius: 10px;
            }
        """)
        msg.setAlignment(Qt.AlignCenter)
        msg.setGeometry(self.rect())
        msg.show()
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, msg.deleteLater)
