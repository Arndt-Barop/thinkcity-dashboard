# settings_screen.py
# Settings-Screen für grundlegende Konfiguration

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QCheckBox, QLineEdit,
                             QComboBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from widgets import StatusBar
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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # StatusBar oben
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Titel-Bereich
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titel
        title = QLabel("Einstellungen")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)
        main_layout.addLayout(title_layout)
        
        # Scroll-Bereich für Settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                width: 25px;
                background: #0a0a0a;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #1e3a5f;
                border-radius: 5px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2c5282;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
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
        
        # === Logging ===
        logging_group = self.create_logging_group()
        scroll_layout.addWidget(logging_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        
        # Layout mit Scroll-Area links und Buttons rechts
        content_layout = QHBoxLayout()
        content_layout.addWidget(scroll, stretch=1)
        
        # Button-Spalte rechts
        button_column = QVBoxLayout()
        button_column.setSpacing(15)
        button_column.setContentsMargins(10, 0, 0, 0)
        
        # Speichern Button
        save_btn = QPushButton("Speichern")
        save_btn.setFont(QFont("Arial", 18, QFont.Bold))
        save_btn.setMinimumSize(150, 100)
        save_btn.clicked.connect(self.on_save)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:pressed {
                background-color: #27ae60;
            }
        """)
        button_column.addWidget(save_btn)
        
        # Abbrechen Button
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setFont(QFont("Arial", 18, QFont.Bold))
        cancel_btn.setMinimumSize(150, 100)
        cancel_btn.clicked.connect(self.on_cancel)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
            }
        """)
        button_column.addWidget(cancel_btn)
        
        button_column.addStretch()
        
        # Neustart Button
        reboot_btn = QPushButton("Neustart")
        reboot_btn.setFont(QFont("Arial", 16, QFont.Bold))
        reboot_btn.setMinimumSize(150, 90)
        reboot_btn.clicked.connect(self.on_reboot)
        reboot_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:pressed {
                background-color: #e67e22;
            }
        """)
        button_column.addWidget(reboot_btn)
        
        # Herunterfahren Button
        shutdown_btn = QPushButton("Herunter-\nfahren")
        shutdown_btn.setFont(QFont("Arial", 16, QFont.Bold))
        shutdown_btn.setMinimumSize(150, 90)
        shutdown_btn.clicked.connect(self.on_shutdown)
        shutdown_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        button_column.addWidget(shutdown_btn)
        
        content_layout.addLayout(button_column)
        
        # Content-Layout zum Haupt-Layout hinzufügen
        main_layout.addLayout(content_layout)
        
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
        group = QGroupBox("CAN-Interface")
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
        """Network Settings (WLAN only)."""
        group = QGroupBox("Network Settings")
        layout = QVBoxLayout()
        
        # === WLAN Configuration ===
        wlan_label = QLabel("WLAN Konfiguration")
        wlan_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 5px;")
        layout.addWidget(wlan_label)
        
        # SSID
        ssid_layout = QHBoxLayout()
        ssid_layout.addWidget(QLabel("SSID:"))
        self.wifi_ssid = QLineEdit(self.settings.get("wifi_ssid", ""))
        self.wifi_ssid.setPlaceholderText("WLAN Name")
        ssid_layout.addWidget(self.wifi_ssid)
        layout.addLayout(ssid_layout)
        
        # Password with Show/Hide
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("Passwort:"))
        self.wifi_password = QLineEdit()
        self.wifi_password.setEchoMode(QLineEdit.Password)
        self.wifi_password.setPlaceholderText("WLAN Passwort (wird verschlüsselt)")
        pwd_layout.addWidget(self.wifi_password)
        
        # Show/Hide Password Button
        self.show_pwd_btn = QPushButton("Show")
        self.show_pwd_btn.setMaximumWidth(60)
        self.show_pwd_btn.setCheckable(True)
        self.show_pwd_btn.clicked.connect(self.toggle_password_visibility)
        pwd_layout.addWidget(self.show_pwd_btn)
        layout.addLayout(pwd_layout)
        
        pwd_info = QLabel("Info: Passwort wird nicht in settings.json gespeichert, nur in NetworkManager")
        pwd_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        pwd_info.setWordWrap(True)
        layout.addWidget(pwd_info)
        
        # === IP Configuration ===
        ip_label = QLabel("IP Konfiguration (nur WLAN)")
        ip_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(ip_label)
        
        # DHCP / Static
        ip_mode_layout = QHBoxLayout()
        ip_mode_layout.addWidget(QLabel("IP-Modus:"))
        self.ip_mode = QComboBox()
        self.ip_mode.addItems(["DHCP (automatisch)", "Static (manuell)"])
        current_mode = self.settings.get("wlan_ip_mode", "dhcp")
        self.ip_mode.setCurrentIndex(0 if current_mode == "dhcp" else 1)
        self.ip_mode.currentIndexChanged.connect(self.on_ip_mode_changed)
        ip_mode_layout.addWidget(self.ip_mode)
        layout.addLayout(ip_mode_layout)
        
        # Static IP Fields Container
        self.static_ip_container = QWidget()
        static_layout = QVBoxLayout()
        static_layout.setContentsMargins(0, 0, 0, 0)
        
        # IP Address with CIDR
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP/CIDR:"))
        self.wlan_ip = QLineEdit(self.settings.get("wlan_ip", "10.42.0.214/24"))
        self.wlan_ip.setPlaceholderText("z.B. 192.168.1.100/24")
        ip_layout.addWidget(self.wlan_ip)
        static_layout.addLayout(ip_layout)
        
        # Gateway
        gw_layout = QHBoxLayout()
        gw_layout.addWidget(QLabel("Gateway:"))
        self.wlan_gateway = QLineEdit(self.settings.get("wlan_gateway", "10.42.0.1"))
        self.wlan_gateway.setPlaceholderText("z.B. 192.168.1.1")
        gw_layout.addWidget(self.wlan_gateway)
        static_layout.addLayout(gw_layout)
        
        # DNS1
        dns1_layout = QHBoxLayout()
        dns1_layout.addWidget(QLabel("DNS 1:"))
        self.wlan_dns1 = QLineEdit(self.settings.get("wlan_dns1", "8.8.8.8"))
        self.wlan_dns1.setPlaceholderText("z.B. 8.8.8.8")
        dns1_layout.addWidget(self.wlan_dns1)
        static_layout.addLayout(dns1_layout)
        
        # DNS2
        dns2_layout = QHBoxLayout()
        dns2_layout.addWidget(QLabel("DNS 2:"))
        self.wlan_dns2 = QLineEdit(self.settings.get("wlan_dns2", "8.8.4.4"))
        self.wlan_dns2.setPlaceholderText("z.B. 8.8.4.4 (optional)")
        dns2_layout.addWidget(self.wlan_dns2)
        static_layout.addLayout(dns2_layout)
        
        # NTP Server
        ntp_layout = QHBoxLayout()
        ntp_layout.addWidget(QLabel("NTP:"))
        self.wlan_ntp = QLineEdit(self.settings.get("wlan_ntp", "pool.ntp.org"))
        self.wlan_ntp.setPlaceholderText("z.B. pool.ntp.org (optional)")
        ntp_layout.addWidget(self.wlan_ntp)
        static_layout.addLayout(ntp_layout)
        
        self.static_ip_container.setLayout(static_layout)
        layout.addWidget(self.static_ip_container)
        
        # Show/Hide static fields based on mode
        self.on_ip_mode_changed(self.ip_mode.currentIndex())
        
        # === WLAN Status ===
        status_label = QLabel("WLAN Status")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(status_label)
        
        self.wlan_status = QLabel("Status wird beim Öffnen geladen...")
        self.wlan_status.setStyleSheet("color: #95a5a6; font-size: 12px;")
        self.wlan_status.setWordWrap(True)
        layout.addWidget(self.wlan_status)
        
        # Update status on opening
        self.update_wlan_status()
        
        # === Sync Setting ===
        self.wifi_only_checkbox = QCheckBox("NAS-Sync nur bei WLAN-Verbindung")
        self.wifi_only_checkbox.setChecked(self.settings.get("sync_on_wifi_only", True))
        self.wifi_only_checkbox.setStyleSheet("margin-top: 10px;")
        layout.addWidget(self.wifi_only_checkbox)
        
        group.setLayout(layout)
        return group
    
    def toggle_password_visibility(self):
        """Toggle WLAN password visibility."""
        if self.show_pwd_btn.isChecked():
            self.wifi_password.setEchoMode(QLineEdit.Normal)
            self.show_pwd_btn.setText("Hide")
        else:
            self.wifi_password.setEchoMode(QLineEdit.Password)
            self.show_pwd_btn.setText("Show")
    
    def toggle_nas_password_visibility(self):
        """Toggle NAS password visibility."""
        if self.show_nas_pwd_btn.isChecked():
            self.nas_password.setEchoMode(QLineEdit.Normal)
            self.show_nas_pwd_btn.setText("Hide")
        else:
            self.nas_password.setEchoMode(QLineEdit.Password)
            self.show_nas_pwd_btn.setText("Show")
    
    def on_ip_mode_changed(self, index):
        """Show/Hide static IP fields based on selection."""
        self.static_ip_container.setVisible(index == 1)  # Show only for Static
    
    def update_wlan_status(self):
        """Update WLAN connection status."""
        import subprocess
        try:
            # Get WLAN device status
            result = subprocess.run(
                ["nmcli", "-t", "-f", "DEVICE,STATE,CONNECTION", "device", "status"],
                capture_output=True, text=True, timeout=2
            )
            
            status_text = "[X] WLAN nicht verbunden"
            for line in result.stdout.strip().split("\n"):
                parts = line.split(":")
                if len(parts) >= 3 and parts[0] == "wlan0":
                    state = parts[1]
                    connection = parts[2]
                    
                    if state == "connected":
                        # Get IP address
                        ip_result = subprocess.run(
                            ["nmcli", "-t", "-f", "IP4.ADDRESS", "device", "show", "wlan0"],
                            capture_output=True, text=True, timeout=2
                        )
                        ip_addr = "N/A"
                        for ip_line in ip_result.stdout.strip().split("\n"):
                            if ip_line.startswith("IP4.ADDRESS"):
                                ip_addr = ip_line.split(":")[1] if ":" in ip_line else "N/A"
                                break
                        
                        status_text = f"[OK] Verbunden mit: {connection}\nIP: {ip_addr}"
                    elif state == "disconnected":
                        status_text = "[X] WLAN getrennt"
                    else:
                        status_text = f"[!] WLAN Status: {state}"
                    break
            
            self.wlan_status.setText(status_text)
            
        except Exception as e:
            self.wlan_status.setText(f"[!] Status konnte nicht geladen werden: {str(e)}")

    
    def create_nas_group(self):
        """NAS Sync Settings."""
        group = QGroupBox("NAS Synchronisation")
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
        
        # NAS Password with Show/Hide
        nas_pwd_layout = QHBoxLayout()
        nas_pwd_layout.addWidget(QLabel("Passwort:"))
        self.nas_password = QLineEdit()
        self.nas_password.setEchoMode(QLineEdit.Password)
        self.nas_password.setPlaceholderText("NAS Passwort (wird verschlüsselt)")
        
        # Load and decrypt existing password if available
        from crypto_utils import get_crypto
        encrypted_pwd = self.settings.get("nas_password_encrypted", "")
        if encrypted_pwd:
            try:
                decrypted = get_crypto().decrypt(encrypted_pwd)
                self.nas_password.setText(decrypted)
            except:
                pass  # Invalid encrypted password, keep empty
        
        nas_pwd_layout.addWidget(self.nas_password)
        
        # Show/Hide Password Button
        self.show_nas_pwd_btn = QPushButton("Show")
        self.show_nas_pwd_btn.setMaximumWidth(60)
        self.show_nas_pwd_btn.setCheckable(True)
        self.show_nas_pwd_btn.clicked.connect(self.toggle_nas_password_visibility)
        nas_pwd_layout.addWidget(self.show_nas_pwd_btn)
        layout.addLayout(nas_pwd_layout)
        
        nas_pwd_info = QLabel("Info: Passwort wird verschlüsselt in settings.json gespeichert")
        nas_pwd_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        layout.addWidget(nas_pwd_info)
        
        info = QLabel("Info: Datenbank wird nach jeder Fahrt automatisch synchronisiert")
        info.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def create_logging_group(self):
        """Logging Settings."""
        from PyQt5.QtWidgets import QSlider, QGridLayout
        
        group = QGroupBox("Datenlogger")
        layout = QVBoxLayout()
        
        # Info: Logging ist immer aktiv
        info_label = QLabel("Info: Daten-Logging ist dauerhaft aktiv")
        info_label.setStyleSheet("color: #95a5a6; font-size: 12px; font-style: italic;")
        layout.addWidget(info_label)
        
        # Datenbankpfad
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(QLabel("Datenbankpfad:"))
        self.db_path = QLineEdit(self.settings["db_path"])
        db_path_layout.addWidget(self.db_path)
        layout.addLayout(db_path_layout)
        
        db_info = QLabel("Info: Standard: /home/pi/thinkcity-dashboard-v3/thinkcity.db")
        db_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        layout.addWidget(db_info)
        
        # Intervall-Slider
        interval_layout = QVBoxLayout()
        interval_label = QLabel(f"Log-Intervall: {self.settings['logging_interval_sec']} Sekunden")
        interval_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
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
        
        interval_info = QLabel("Info: 1s = hohe Genauigkeit, hoher Speicher | 60s = niedrige Genauigkeit, wenig Speicher")
        interval_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        interval_info.setWordWrap(True)
        interval_layout.addWidget(interval_info)
        
        layout.addLayout(interval_layout)
        
        # Datenpunkt-Auswahl
        fields_label = QLabel("Zu loggende Datenpunkte:")
        fields_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(fields_label)
        
        # Dauerhaft aktive Felder (nicht abwählbar)
        permanent_label = QLabel("Ø Durchschnittsverbrauch - Dauerhaft aktiv")
        permanent_label.setStyleSheet("font-size: 12px; color: #95a5a6; font-style: italic; margin-left: 5px;")
        layout.addWidget(permanent_label)
        
        # Alle verfügbaren Felder
        available_fields = {
            "speed_kmh": "Geschwindigkeit",
            "soc_pct": "Ladezustand (SOC)",
            "voltage_V": "Spannung",
            "current_A": "Strom",
            "power_kW": "Leistung",
            "pack_temp_C": "Akku-Temperatur",
            "ambient_temp_C": "Außentemperatur",
            "consumption_wh_km": "Verbrauch Wh/km",
            "range_km": "Reichweite",
            "odo_km": "Kilometerstand",
            "latitude": "GPS Breitengrad",
            "longitude": "GPS Längengrad"
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
        
        select_all_btn = QPushButton("Alle")
        select_all_btn.setMaximumWidth(100)
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in self.field_checkboxes.values()])
        select_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Keine")
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
        
        # WLAN IP Configuration
        self.settings["wlan_ip_mode"] = "dhcp" if self.ip_mode.currentIndex() == 0 else "static"
        self.settings["wlan_ip"] = self.wlan_ip.text()
        self.settings["wlan_gateway"] = self.wlan_gateway.text()
        self.settings["wlan_dns1"] = self.wlan_dns1.text()
        self.settings["wlan_dns2"] = self.wlan_dns2.text()
        self.settings["wlan_ntp"] = self.wlan_ntp.text()
        
        self.settings["nas_sync_enabled"] = self.nas_enable.isChecked()
        self.settings["nas_host"] = self.nas_host.text()
        self.settings["nas_path"] = self.nas_path.text()
        self.settings["nas_user"] = self.nas_user.text()
        
        # Encrypt and save NAS password
        from crypto_utils import get_crypto
        nas_pwd = self.nas_password.text().strip()
        if nas_pwd:
            self.settings["nas_password_encrypted"] = get_crypto().encrypt(nas_pwd)
        else:
            self.settings["nas_password_encrypted"] = ""
        
        self.settings["db_path"] = self.db_path.text()
        
        # Logging Settings (logging ist immer aktiviert)
        self.settings["logging_enabled"] = True  # Dauerhaft aktiv
        self.settings["logging_interval_sec"] = self.logging_interval_slider.value()
        self.settings["logging_fields"] = [
            field_name for field_name, checkbox in self.field_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        self.save_settings()
        
        # Handle CAN-Simulation Service
        if self.settings["simulation_mode"]:
            # Aktiviere und starte CAN-Simulation Service
            self._enable_can_simulation()
        else:
            # Deaktiviere CAN-Simulation Service
            self._disable_can_simulation()
        
        # Apply WLAN Configuration via NetworkManager
        self._apply_wlan_config()
        
        # Zeige Bestätigung
        self.show_message("[OK] Einstellungen gespeichert!\n\nNeustart erforderlich für CAN-Interface Änderung.")
    
    def _apply_wlan_config(self):
        """Apply WLAN configuration via NetworkManager."""
        import subprocess
        
        ssid = self.wifi_ssid.text().strip()
        password = self.wifi_password.text().strip()
        
        if not ssid:
            return  # No SSID, skip configuration
        
        try:
            # Check if connection already exists
            check_cmd = ["nmcli", "-t", "-f", "NAME", "connection", "show"]
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            existing_connections = result.stdout.strip().split("\n")
            
            # Delete existing connection with same SSID
            if ssid in existing_connections:
                subprocess.run(["nmcli", "connection", "delete", ssid], timeout=5)
            
            # Build nmcli command
            cmd = [
                "nmcli", "connection", "add",
                "type", "wifi",
                "ifname", "wlan0",
                "con-name", ssid,
                "ssid", ssid
            ]
            
            # Add password if provided
            if password:
                cmd.extend(["wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password])
            
            # Add IP configuration
            if self.settings["wlan_ip_mode"] == "static":
                ip_addr = self.wlan_ip.text().strip()
                gateway = self.wlan_gateway.text().strip()
                dns1 = self.wlan_dns1.text().strip()
                dns2 = self.wlan_dns2.text().strip()
                
                cmd.extend([
                    "ipv4.method", "manual",
                    "ipv4.addresses", ip_addr,
                    "ipv4.gateway", gateway
                ])
                
                # Add DNS servers
                dns_servers = dns1
                if dns2:
                    dns_servers += f",{dns2}"
                cmd.extend(["ipv4.dns", dns_servers])
            else:
                cmd.extend(["ipv4.method", "auto"])
            
            # Create connection
            subprocess.run(cmd, timeout=10, check=True)
            
            # Try to activate connection
            subprocess.run(["nmcli", "connection", "up", ssid], timeout=15)
            
            # Update status display
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.update_wlan_status)
            
        except subprocess.TimeoutExpired:
            self.show_message("[!] WLAN-Konfiguration: Zeitüberschreitung")
        except subprocess.CalledProcessError as e:
            self.show_message(f"[!] WLAN-Konfiguration fehlgeschlagen:\n{e}")
        except Exception as e:
            self.show_message(f"[!] Fehler bei WLAN-Konfiguration:\n{str(e)}")
    
    def on_cancel(self):
        """Verwerfe Änderungen."""
        self.settings = self.load_settings()
        self.show_message("[X] Änderungen verworfen")
    
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
    
    def _enable_can_simulation(self):
        """Aktiviere und starte CAN-Simulation Service."""
        import subprocess
        try:
            # Enable Service
            subprocess.run(['sudo', 'systemctl', 'enable', 'can-simulation'], check=True)
            print("✓ CAN-Simulation Service aktiviert")
        except subprocess.CalledProcessError as e:
            print(f"✗ Fehler beim Aktivieren: {e}")
    
    def _disable_can_simulation(self):
        """Deaktiviere CAN-Simulation Service."""
        import subprocess
        try:
            # Disable Service
            subprocess.run(['sudo', 'systemctl', 'disable', 'can-simulation'], check=True)
            # Stop Service (falls läuft)
            subprocess.run(['sudo', 'systemctl', 'stop', 'can-simulation'], check=False)
            print("✓ CAN-Simulation Service deaktiviert")
        except subprocess.CalledProcessError as e:
            print(f"✗ Fehler beim Deaktivieren: {e}")


# Test-Programm
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    screen = SettingsScreen()
    screen.show()
    sys.exit(app.exec_())
