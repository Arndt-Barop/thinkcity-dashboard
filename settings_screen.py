# settings_screen.py
# Settings screen for basic configuration

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QCheckBox, QLineEdit,
                             QComboBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from widgets import StatusBar
from translations import get_translator
from trace_player import TracePlayer
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
        self.translator = get_translator()
        self.translator.set_language(self.settings.get("language", "DE"))
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
            "language": "DE",
            # Logging Settings
            "logging_enabled": True,
            "logging_interval_sec": 1,
            "logging_fields": [
                # Basic (commonly used)
                "speed_kmh", "soc_pct", "voltage_V", "current_A", "power_kW",
                "pack_temp_C", "ambient_temp_C", "consumption_wh_km", "range_km", "odo_km",
                # EnerDel battery health
                "e_pack_max_cell_V", "e_pack_min_cell_V", "e_pack_avg_cell_V", "e_pack_delta_cell_V",
                "e_pack_max_temp_C", "e_pack_min_temp_C",
                # Module voltages
                "module1_voltage_V", "module2_voltage_V", "module3_voltage_V", "module4_voltage_V",
                # Error flags (always useful for diagnostics)
                "iso_error", "emergency", "sys_int_iso_error", "sys_ext_iso_error", "sys_thermal_iso_error"
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
        t = self.translator.get  # Shortcut for translations
        
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
        title = QLabel(t("settings"))
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)
        main_layout.addLayout(title_layout)
        
        # Scroll area for settings
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
        
        # === Language ===
        language_group = self.create_language_group()
        scroll_layout.addWidget(language_group)
        
        # === Trip Computer ===
        trip_group = self.create_trip_computer_group()
        scroll_layout.addWidget(trip_group)
        
        # === Trace Replay ===
        trace_group = self.create_trace_replay_group()
        scroll_layout.addWidget(trace_group)
        
        # === Trace Recording ===
        recording_group = self.create_trace_recording_group()
        scroll_layout.addWidget(recording_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        
        # Layout with scroll area left und Buttons rechts
        content_layout = QHBoxLayout()
        content_layout.addWidget(scroll, stretch=1)
        
        # Button column right
        button_column = QVBoxLayout()
        button_column.setSpacing(15)
        button_column.setContentsMargins(10, 0, 0, 0)
        
        # Save button
        save_btn = QPushButton(t("save"))
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
        
        # Cancel button
        cancel_btn = QPushButton(t("cancel"))
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
        reboot_btn = QPushButton(t("reboot"))
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
        shutdown_btn = QPushButton(t("shutdown"))
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
        
        # Add content layout to main layout
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
        t = self.translator.get
        
        group = QGroupBox(t("can_interface"))
        layout = QVBoxLayout()
        
        # Interface Auswahl
        interface_layout = QHBoxLayout()
        interface_layout.addWidget(QLabel(t("interface") + ":"))
        
        self.can_combo = QComboBox()
        self.can_combo.addItems(["can0", "vcan0"])
        self.can_combo.setCurrentText(self.settings["can_interface"])
        interface_layout.addWidget(self.can_combo)
        layout.addLayout(interface_layout)
        
        # Simulation Mode
        self.sim_checkbox = QCheckBox(t("simulation_mode_label"))
        self.sim_checkbox.setChecked(self.settings["simulation_mode"])
        layout.addWidget(self.sim_checkbox)
        
        info = QLabel(t("simulation_info"))
        info.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def create_wifi_group(self):
        """Network Settings (WLAN only)."""
        t = self.translator.get
        
        group = QGroupBox(t("network_settings"))
        layout = QVBoxLayout()
        
        # === WLAN Configuration ===
        wlan_label = QLabel(t("wlan_config"))
        wlan_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 5px;")
        layout.addWidget(wlan_label)
        
        # SSID
        ssid_layout = QHBoxLayout()
        ssid_layout.addWidget(QLabel(t("ssid") + ":"))
        self.wifi_ssid = QLineEdit(self.settings.get("wifi_ssid", ""))
        self.wifi_ssid.setPlaceholderText(t("ssid_placeholder"))
        ssid_layout.addWidget(self.wifi_ssid)
        layout.addLayout(ssid_layout)
        
        # Password with Show/Hide
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel(t("password") + ":"))
        self.wifi_password = QLineEdit()
        self.wifi_password.setEchoMode(QLineEdit.Password)
        self.wifi_password.setPlaceholderText(t("password_placeholder"))
        
        # Load encrypted WiFi password
        from crypto_utils import get_crypto
        encrypted_wifi_pwd = self.settings.get("wifi_password_encrypted", "")
        if encrypted_wifi_pwd:
            try:
                decrypted_pwd = get_crypto().decrypt(encrypted_wifi_pwd)
                self.wifi_password.setText(decrypted_pwd)
            except Exception as e:
                print(f"Warning: Could not decrypt WiFi password: {e}")
        
        pwd_layout.addWidget(self.wifi_password)
        
        # Show/Hide Password Button
        self.show_pwd_btn = QPushButton(t("show"))
        self.show_pwd_btn.setMaximumWidth(60)
        self.show_pwd_btn.setCheckable(True)
        self.show_pwd_btn.clicked.connect(self.toggle_password_visibility)
        pwd_layout.addWidget(self.show_pwd_btn)
        layout.addLayout(pwd_layout)
        
        pwd_info = QLabel(t("password_info"))
        pwd_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        pwd_info.setWordWrap(True)
        layout.addWidget(pwd_info)
        
        # === IP Configuration ===
        ip_label = QLabel(t("ip_config"))
        ip_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(ip_label)
        
        # DHCP / Static
        ip_mode_layout = QHBoxLayout()
        ip_mode_layout.addWidget(QLabel(t("ip_mode") + ":"))
        self.ip_mode = QComboBox()
        self.ip_mode.addItems([t("dhcp_auto"), t("static_manual")])
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
        ip_layout.addWidget(QLabel(t("ip_cidr") + ":"))
        self.wlan_ip = QLineEdit(self.settings.get("wlan_ip", "10.42.0.214/24"))
        self.wlan_ip.setPlaceholderText(t("ip_placeholder"))
        ip_layout.addWidget(self.wlan_ip)
        static_layout.addLayout(ip_layout)
        
        # Gateway
        gw_layout = QHBoxLayout()
        gw_layout.addWidget(QLabel(t("gateway") + ":"))
        self.wlan_gateway = QLineEdit(self.settings.get("wlan_gateway", "10.42.0.1"))
        self.wlan_gateway.setPlaceholderText(t("gateway_placeholder"))
        gw_layout.addWidget(self.wlan_gateway)
        static_layout.addLayout(gw_layout)
        
        # DNS1
        dns1_layout = QHBoxLayout()
        dns1_layout.addWidget(QLabel(t("dns1") + ":"))
        self.wlan_dns1 = QLineEdit(self.settings.get("wlan_dns1", "8.8.8.8"))
        self.wlan_dns1.setPlaceholderText(t("dns1_placeholder"))
        dns1_layout.addWidget(self.wlan_dns1)
        static_layout.addLayout(dns1_layout)
        
        # DNS2
        dns2_layout = QHBoxLayout()
        dns2_layout.addWidget(QLabel(t("dns2") + ":"))
        self.wlan_dns2 = QLineEdit(self.settings.get("wlan_dns2", "8.8.4.4"))
        self.wlan_dns2.setPlaceholderText(t("dns2_placeholder"))
        dns2_layout.addWidget(self.wlan_dns2)
        static_layout.addLayout(dns2_layout)
        
        # NTP Server
        ntp_layout = QHBoxLayout()
        ntp_layout.addWidget(QLabel(t("ntp") + ":"))
        self.wlan_ntp = QLineEdit(self.settings.get("wlan_ntp", "pool.ntp.org"))
        self.wlan_ntp.setPlaceholderText(t("ntp_placeholder"))
        ntp_layout.addWidget(self.wlan_ntp)
        static_layout.addLayout(ntp_layout)
        
        self.static_ip_container.setLayout(static_layout)
        layout.addWidget(self.static_ip_container)
        
        # Show/Hide static fields based on mode
        self.on_ip_mode_changed(self.ip_mode.currentIndex())
        
        # === WLAN Status ===
        status_label = QLabel(t("wlan_status"))
        status_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(status_label)
        
        self.wlan_status = QLabel(t("status_loading"))
        self.wlan_status.setStyleSheet("color: #95a5a6; font-size: 12px;")
        self.wlan_status.setWordWrap(True)
        layout.addWidget(self.wlan_status)
        
        # Update status on opening
        self.update_wlan_status()
        
        # === Sync Setting ===
        self.wifi_only_checkbox = QCheckBox(t("sync_wifi_only"))
        self.wifi_only_checkbox.setChecked(self.settings.get("sync_on_wifi_only", True))
        self.wifi_only_checkbox.setStyleSheet("margin-top: 10px;")
        layout.addWidget(self.wifi_only_checkbox)
        
        group.setLayout(layout)
        return group
    
    def toggle_password_visibility(self):
        """Toggle WLAN password visibility."""
        t = self.translator.get
        if self.show_pwd_btn.isChecked():
            self.wifi_password.setEchoMode(QLineEdit.Normal)
            self.show_pwd_btn.setText(t("hide"))
        else:
            self.wifi_password.setEchoMode(QLineEdit.Password)
            self.show_pwd_btn.setText(t("show"))
    
    def toggle_nas_password_visibility(self):
        """Toggle NAS password visibility."""
        t = self.translator.get
        if self.show_nas_pwd_btn.isChecked():
            self.nas_password.setEchoMode(QLineEdit.Normal)
            self.show_nas_pwd_btn.setText(t("hide"))
        else:
            self.nas_password.setEchoMode(QLineEdit.Password)
            self.show_nas_pwd_btn.setText(t("show"))
    
    def on_ip_mode_changed(self, index):
        """Show/Hide static IP fields based on selection."""
        self.static_ip_container.setVisible(index == 1)  # Show only for Static
    
    def update_wlan_status(self):
        """Update WLAN connection status."""
        import subprocess
        t = self.translator.get
        
        try:
            # Get WLAN device status
            result = subprocess.run(
                ["nmcli", "-t", "-f", "DEVICE,STATE,CONNECTION", "device", "status"],
                capture_output=True, text=True, timeout=2
            )
            
            status_text = t("wlan_not_connected")
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
                        
                        status_text = f"{t('wlan_connected')}: {connection}\nIP: {ip_addr}"
                    elif state == "disconnected":
                        status_text = t("wlan_disconnected")
                    else:
                        status_text = f"[!] {t('wlan_status')}: {state}"
                    break
            
            self.wlan_status.setText(status_text)
            
        except Exception as e:
            self.wlan_status.setText(f"[!] {t('wlan_status')}: {str(e)}")

    
    def create_nas_group(self):
        """NAS Sync Settings."""
        t = self.translator.get
        
        group = QGroupBox(t("nas_sync"))
        layout = QVBoxLayout()
        
        # Enable Sync
        self.nas_enable = QCheckBox(t("nas_enable"))
        self.nas_enable.setChecked(self.settings["nas_sync_enabled"])
        layout.addWidget(self.nas_enable)
        
        # NAS Host
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel(t("nas_host") + ":"))
        self.nas_host = QLineEdit(self.settings["nas_host"])
        self.nas_host.setPlaceholderText(t("nas_host_placeholder"))
        host_layout.addWidget(self.nas_host)
        layout.addLayout(host_layout)
        
        # NAS Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel(t("nas_path") + ":"))
        self.nas_path = QLineEdit(self.settings["nas_path"])
        self.nas_path.setPlaceholderText(t("nas_path_placeholder"))
        path_layout.addWidget(self.nas_path)
        layout.addLayout(path_layout)
        
        # NAS User
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel(t("nas_user") + ":"))
        self.nas_user = QLineEdit(self.settings["nas_user"])
        self.nas_user.setPlaceholderText(t("nas_user_placeholder"))
        user_layout.addWidget(self.nas_user)
        layout.addLayout(user_layout)
        
        # NAS Password with Show/Hide
        nas_pwd_layout = QHBoxLayout()
        nas_pwd_layout.addWidget(QLabel(t("password") + ":"))
        self.nas_password = QLineEdit()
        self.nas_password.setEchoMode(QLineEdit.Password)
        self.nas_password.setPlaceholderText(t("nas_password_placeholder"))
        
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
        self.show_nas_pwd_btn = QPushButton(t("show"))
        self.show_nas_pwd_btn.setMaximumWidth(60)
        self.show_nas_pwd_btn.setCheckable(True)
        self.show_nas_pwd_btn.clicked.connect(self.toggle_nas_password_visibility)
        nas_pwd_layout.addWidget(self.show_nas_pwd_btn)
        layout.addLayout(nas_pwd_layout)
        
        nas_pwd_info = QLabel(t("nas_password_info"))
        nas_pwd_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        layout.addWidget(nas_pwd_info)
        
        info = QLabel(t("nas_sync_info"))
        info.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def create_logging_group(self):
        """Logging Settings."""
        from PyQt5.QtWidgets import QSlider, QGridLayout
        t = self.translator.get
        
        group = QGroupBox(t("data_logger"))
        layout = QVBoxLayout()
        
        # Info: Logging ist immer aktiv
        info_label = QLabel(t("logging_always_active"))
        info_label.setStyleSheet("color: #95a5a6; font-size: 12px; font-style: italic;")
        layout.addWidget(info_label)
        
        # Datenbankpfad
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(QLabel(t("db_path") + ":"))
        self.db_path = QLineEdit(self.settings["db_path"])
        db_path_layout.addWidget(self.db_path)
        layout.addLayout(db_path_layout)
        
        db_info = QLabel(t("db_path_info"))
        db_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        layout.addWidget(db_info)
        
        # Intervall-Slider
        interval_layout = QVBoxLayout()
        interval_label = QLabel(f"{t('log_interval')}: {self.settings['logging_interval_sec']} {t('seconds')}")
        interval_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        interval_layout.addWidget(interval_label)
        
        self.logging_interval_slider = QSlider(Qt.Horizontal)
        self.logging_interval_slider.setMinimum(1)
        self.logging_interval_slider.setMaximum(60)
        self.logging_interval_slider.setValue(self.settings["logging_interval_sec"])
        self.logging_interval_slider.setTickPosition(QSlider.TicksBelow)
        self.logging_interval_slider.setTickInterval(5)
        
        def update_interval_label(value):
            interval_label.setText(f"{t('log_interval')}: {value} {t('seconds')}")
        
        self.logging_interval_slider.valueChanged.connect(update_interval_label)
        interval_layout.addWidget(self.logging_interval_slider)
        
        interval_info = QLabel(t("interval_info"))
        interval_info.setStyleSheet("color: #95a5a6; font-size: 11px;")
        interval_info.setWordWrap(True)
        interval_layout.addWidget(interval_info)
        
        layout.addLayout(interval_layout)
        
        # Datenpunkt-Auswahl
        fields_label = QLabel(t("data_points") + ":")
        fields_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(fields_label)
        
        # Permanently active fields (not deselectable)
        permanent_label = QLabel(t("avg_consumption_permanent") + " + SOH")
        permanent_label.setStyleSheet("font-size: 12px; color: #95a5a6; font-style: italic; margin-left: 5px;")
        layout.addWidget(permanent_label)
        
        # All available fields (organized by category)
        available_fields = {
            # Basic driving data
            "speed_kmh": t("field_speed"),
            "soc_pct": t("field_soc"),
            "range_km": t("field_range"),
            "odo_km": t("field_odo"),
            
            # Power & Energy
            "voltage_V": t("field_voltage"),
            "current_A": t("field_current"),
            "power_kW": t("field_power"),
            "consumption_wh_km": t("field_consumption"),
            
            # Temperatures
            "pack_temp_C": t("field_pack_temp"),
            "ambient_temp_C": t("field_ambient_temp"),
            "e_pack_max_temp_C": "EnerDel Max Temp (°C)",
            "e_pack_min_temp_C": "EnerDel Min Temp (°C)",
            
            # Cell Voltages (EnerDel)
            "e_pack_max_cell_V": "Zellspannung Max (V)",
            "e_pack_min_cell_V": "Zellspannung Min (V)",
            "e_pack_avg_cell_V": "Zellspannung Avg (V)",
            "e_pack_delta_cell_V": "Zellspannung Delta (V)",
            
            # Module Voltages
            "module1_voltage_V": "Modul 1 Spannung (V)",
            "module2_voltage_V": "Modul 2 Spannung (V)",
            "module3_voltage_V": "Modul 3 Spannung (V)",
            "module4_voltage_V": "Modul 4 Spannung (V)",
            "modules_total_V": "Module Gesamt (V)",
            
            # Error Flags
            "iso_error": "ISO-Fehler",
            "emergency": "Notfall",
            "sys_int_iso_error": "System Int ISO-Fehler",
            "sys_ext_iso_error": "System Ext ISO-Fehler",
            "sys_thermal_iso_error": "System Thermal ISO-Fehler",
        }
        
        # Grid for checkboxes (2 columns)
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
        
        # Buttons for all/none
        select_layout = QHBoxLayout()
        
        select_all_btn = QPushButton(t("select_all"))
        select_all_btn.setMaximumWidth(100)
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in self.field_checkboxes.values()])
        select_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton(t("select_none"))
        select_none_btn.setMaximumWidth(100)
        select_none_btn.clicked.connect(lambda: [cb.setChecked(False) for cb in self.field_checkboxes.values()])
        select_layout.addWidget(select_none_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        group.setLayout(layout)
        return group
    
    def create_language_group(self):
        """Language Settings."""
        t = self.translator.get
        
        group = QGroupBox(t("language_settings"))
        layout = QVBoxLayout()
        
        # Language Selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(t("language") + ":"))
        
        self.language_combo = QComboBox()
        self.language_combo.addItems([t("language_german"), t("language_english")])
        current_lang = self.settings.get("language", "DE")
        self.language_combo.setCurrentIndex(0 if current_lang == "DE" else 1)
        lang_layout.addWidget(self.language_combo)
        
        layout.addLayout(lang_layout)
        
        group.setLayout(layout)
        return group
    
    def create_trip_computer_group(self):
        """Trip Computer Settings."""
        t = self.translator.get
        
        group = QGroupBox(t("trip_computer"))
        layout = QVBoxLayout()
        
        # Reset Consumption Button
        reset_consumption_layout = QHBoxLayout()
        reset_consumption_btn = QPushButton(t("reset_consumption"))
        reset_consumption_btn.setMinimumHeight(50)
        reset_consumption_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        reset_consumption_btn.clicked.connect(self.on_reset_consumption)
        reset_consumption_layout.addWidget(reset_consumption_btn)
        layout.addLayout(reset_consumption_layout)
        
        # Info text for consumption
        info_consumption_label = QLabel(t("reset_consumption") + ": " + 
                           ("Setzt den gespeicherten Durchschnittsverbrauch zurück" if t("language") == "DE" 
                            else "Resets the stored average consumption"))
        info_consumption_label.setWordWrap(True)
        info_consumption_label.setStyleSheet("color: #888888; font-size: 11px; margin-bottom: 15px;")
        layout.addWidget(info_consumption_label)
        
        # Reset SOH Button
        reset_soh_layout = QHBoxLayout()
        reset_soh_btn = QPushButton("SOH " + ("zurücksetzen" if t("language") == "DE" else "Reset"))
        reset_soh_btn.setMinimumHeight(50)
        reset_soh_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        reset_soh_btn.clicked.connect(self.on_reset_soh)
        reset_soh_layout.addWidget(reset_soh_btn)
        layout.addLayout(reset_soh_layout)
        
        # Info text for SOH
        info_soh_label = QLabel("SOH: " + 
                           ("Setzt den State of Health auf 100% zurück (nach Batterietausch)" if t("language") == "DE" 
                            else "Resets State of Health to 100% (after battery replacement)"))
        info_soh_label.setWordWrap(True)
        info_soh_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(info_soh_label)
        
        group.setLayout(layout)
        return group
    
    def create_trace_replay_group(self):
        """Trace Replay Settings."""
        t = self.translator.get
        
        group = QGroupBox(t("trace_replay"))
        layout = QVBoxLayout()
        
        # Trace File Selection
        trace_layout = QHBoxLayout()
        trace_label = QLabel(t("select_trace") + ":")
        trace_label.setMinimumWidth(150)
        trace_layout.addWidget(trace_label)
        
        self.trace_combo = QComboBox()
        self.trace_combo.setMinimumHeight(40)
        self._scan_trace_files()
        trace_layout.addWidget(self.trace_combo, stretch=1)
        layout.addLayout(trace_layout)
        
        # Loop Playback Checkbox
        self.loop_checkbox = QCheckBox(t("loop_playback"))
        self.loop_checkbox.setChecked(self.settings.get("trace_loop", False))
        layout.addWidget(self.loop_checkbox)
                # Start/Pause/Stop Buttons
        self.trace_start_btn = QPushButton("Start")
        self.trace_pause_btn = QPushButton("Pause")
        self.trace_stop_btn = QPushButton("Stop")
        self.trace_status_label = QLabel("Status: Stopped")
        layout.addWidget(self.trace_start_btn)
        layout.addWidget(self.trace_pause_btn)
        layout.addWidget(self.trace_stop_btn)
        layout.addWidget(self.trace_status_label)

        self.trace_start_btn.clicked.connect(self.on_trace_start)
        self.trace_pause_btn.clicked.connect(self.on_trace_pause)
        self.trace_stop_btn.clicked.connect(self.on_trace_stop)

        # Info text
        info_label = QLabel(t("trace_info"))
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888888; font-size: 11px; margin-top: 10px;")
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group

    def on_trace_start(self):
        trace_file = self.trace_combo.currentData()
        if not trace_file:
            self.trace_status_label.setText("Status: No trace selected")
            return
        self.trace_player = TracePlayer(interface='vcan0')
        self.trace_player.load_trace(trace_file)
        self.trace_player.connect()
        self.trace_player.start(loop=self.loop_checkbox.isChecked())
        self.trace_status_label.setText("Status: Playing")

    def on_trace_pause(self):
        if self.trace_player and self.trace_player.is_playing:
            self.trace_player.pause()
            self.trace_status_label.setText("Status: Paused")

    def on_trace_stop(self):
        if self.trace_player:
            self.trace_player.stop()
            self.trace_player.disconnect()
            self.trace_status_label.setText("Status: Stopped")
            
    def _scan_trace_files(self):
        """Scan traces/ directory nach .trc Dateien."""
        import os
        t = self.translator.get
        
        traces_dir = os.path.expanduser("~/thinkcity-dashboard-v3/traces")
        self.trace_combo.clear()
        
        # "Keine Auswahl" Option
        self.trace_combo.addItem(t("no_trace_selected"), "")
        
        if not os.path.exists(traces_dir):
            self.trace_combo.addItem(t("no_traces_found"), "")
            return
        
        # Find all .trc files
        trace_files = sorted([f for f in os.listdir(traces_dir) if f.endswith('.trc')])
        
        if not trace_files:
            self.trace_combo.addItem(t("no_traces_found"), "")
            return
        
        # Add trace files
        for trace_file in trace_files:
            full_path = os.path.join(traces_dir, trace_file)
            self.trace_combo.addItem(trace_file, full_path)
        
        # Select saved trace aus
        saved_trace = self.settings.get("trace_file", "")
        if saved_trace:
            index = self.trace_combo.findData(saved_trace)
            if index >= 0:
                self.trace_combo.setCurrentIndex(index)
    
    def create_trace_recording_group(self):
        """Trace Recording Controls."""
        t = self.translator.get
        
        group = QGroupBox(t("can_trace_recording"))
        layout = QVBoxLayout()
        
        # Status display
        self.recording_status_label = QLabel(t("not_recording"))
        self.recording_status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.recording_status_label)
        
        # Statistics (während Aufnahme)
        self.recording_stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.recording_stats_widget)
        stats_layout.setContentsMargins(10, 5, 10, 5)
        stats_layout.setSpacing(5)
        
        self.recording_duration_label = QLabel(f"{t('duration')}: 00:00:00")
        self.recording_duration_label.setStyleSheet("font-size: 12px; color: #888;")
        stats_layout.addWidget(self.recording_duration_label)
        
        self.recording_messages_label = QLabel(f"{t('messages')}: 0")
        self.recording_messages_label.setStyleSheet("font-size: 12px; color: #888;")
        stats_layout.addWidget(self.recording_messages_label)
        
        self.recording_filesize_label = QLabel(f"{t('file_size')}: 0 KB")
        self.recording_filesize_label.setStyleSheet("font-size: 12px; color: #888;")
        stats_layout.addWidget(self.recording_filesize_label)
        
        self.recording_stats_widget.setVisible(False)  # Hidden until recording starts
        layout.addWidget(self.recording_stats_widget)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.record_start_btn = QPushButton(t("start_recording"))
        self.record_start_btn.setMinimumHeight(50)
        self.record_start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.record_start_btn.clicked.connect(self.on_start_recording)
        buttons_layout.addWidget(self.record_start_btn)
        
        self.record_stop_btn = QPushButton(t("stop_recording"))
        self.record_stop_btn.setMinimumHeight(50)
        self.record_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.record_stop_btn.clicked.connect(self.on_stop_recording)
        self.record_stop_btn.setEnabled(False)  # Disabled until recording starts
        buttons_layout.addWidget(self.record_stop_btn)
        
        layout.addLayout(buttons_layout)
        
        # Filename preview
        self.recording_filename_label = QLabel()
        self.recording_filename_label.setStyleSheet("font-size: 11px; color: #888; margin-top: 10px;")
        self.recording_filename_label.setWordWrap(True)
        self._update_recording_filename_preview()
        layout.addWidget(self.recording_filename_label)
        
        # Storage info
        self.recording_storage_label = QLabel()
        self.recording_storage_label.setStyleSheet("font-size: 11px; color: #888;")
        self._update_storage_info()
        layout.addWidget(self.recording_storage_label)
        
        group.setLayout(layout)
        return group
    
    def _update_recording_filename_preview(self):
        """Update filename preview with next expected filename."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"ThinkCity_{timestamp}.trc"
        t = self.translator.get
        self.recording_filename_label.setText(f"{t('filename')}: {filename}")
    
    def _update_storage_info(self):
        """Update storage space information."""
        try:
            import os
            traces_dir = os.path.expanduser("~/thinkcity-dashboard-v3/traces")
            st = os.statvfs(traces_dir)
            free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
            t = self.translator.get
            self.recording_storage_label.setText(f"{t('storage_location')}: {free_gb:.1f} GB free (traces/)")
        except Exception as e:
            self.recording_storage_label.setText(f"Storage: Unknown ({e})")
    
    def on_start_recording(self):
        """Start trace recording."""
        print("[DEBUG] on_start_recording() called")
        
        # Navigate from SettingsScreen -> QStackedWidget -> Dashboard
        stacked_widget = self.parent()
        print(f"[DEBUG] stacked_widget = {stacked_widget}")
        
        if stacked_widget is None:
            print("[ERROR] parent() returned None!")
            return
        
        dashboard = stacked_widget.parent()
        print(f"[DEBUG] dashboard = {dashboard}")
        
        if dashboard is None:
            print("[ERROR] dashboard (grandparent) is None!")
            return
            
        if not hasattr(dashboard, 'trace_recorder'):
            print(f"[ERROR] dashboard has no attribute 'trace_recorder'. Type: {type(dashboard)}")
            return
            
        print(f"[DEBUG] trace_recorder = {dashboard.trace_recorder}")
        
        try:
            result = dashboard.trace_recorder.start_recording()
            print(f"[DEBUG] start_recording() returned: {result}")
            
            if result:
                # Update UI
                t = self.translator.get
                self.recording_status_label.setText(f"[REC] {t('recording_active')}")
                self.recording_status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; color: #e74c3c;")
                self.recording_stats_widget.setVisible(True)
                self.record_start_btn.setEnabled(False)
                self.record_stop_btn.setEnabled(True)
                
                # Start timer to update stats
                from PyQt5.QtCore import QTimer
                self.recording_stats_timer = QTimer(self)
                self.recording_stats_timer.timeout.connect(self._update_recording_stats)
                self.recording_stats_timer.start(1000)  # Update every second
                print("[SUCCESS] Recording started successfully")
            else:
                print("[ERROR] start_recording() returned False")
                t = self.translator.get
                self.show_message("Failed to start recording" if t("language") == "EN" else "Aufnahme konnte nicht gestartet werden")
        except Exception as e:
            print(f"[ERROR] Exception in on_start_recording: {e}")
            import traceback
            traceback.print_exc()

    
    def on_stop_recording(self):
        """Stop trace recording."""
        # Navigate from SettingsScreen -> QStackedWidget -> Dashboard
        stacked_widget = self.parent()
        if stacked_widget is None:
            print("Warning: Could not access parent")
            return
            
        dashboard = stacked_widget.parent()
        if dashboard and hasattr(dashboard, 'trace_recorder'):
            stats = dashboard.trace_recorder.stop_recording()
            
            # Stop stats timer
            if hasattr(self, 'recording_stats_timer'):
                self.recording_stats_timer.stop()
            
            # Update UI
            t = self.translator.get
            self.recording_status_label.setText(t("not_recording"))
            self.recording_status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
            self.recording_stats_widget.setVisible(False)
            self.record_start_btn.setEnabled(True)
            self.record_stop_btn.setEnabled(False)
            
            # Update filename preview for next recording
            self._update_recording_filename_preview()
            self._update_storage_info()
            
            # Show completion message with stats
            if stats:
                message = (
                    f"{t('recording_stopped')}\n\n"
                    f"{t('filename')}: {stats.get('filename', 'N/A')}\n"
                    f"{t('duration')}: {stats.get('duration_seconds', 0):.1f}s\n"
                    f"{t('messages')}: {stats.get('message_count', 0)}\n"
                    f"{t('file_size')}: {stats.get('file_size_mb', 0):.2f} MB"
                )
                self.show_message(message)
        else:
            print("Warning: Could not access trace_recorder from parent")
    
    def _update_recording_stats(self):
        """Update recording statistics display (called by timer)."""
        # Navigate from SettingsScreen -> QStackedWidget -> Dashboard
        stacked_widget = self.parent()
        if stacked_widget is None:
            return
            
        dashboard = stacked_widget.parent()
        if dashboard and hasattr(dashboard, 'trace_recorder'):
            stats = dashboard.trace_recorder.get_stats()
            if stats:
                # Duration
                duration_sec = stats.get('duration_seconds', 0)
                hours = int(duration_sec // 3600)
                minutes = int((duration_sec % 3600) // 60)
                seconds = int(duration_sec % 60)
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                t = self.translator.get
                self.recording_duration_label.setText(f"{t('duration')}: {duration_str}")
                
                # Messages
                msg_count = stats.get('message_count', 0)
                self.recording_messages_label.setText(f"{t('messages')}: {msg_count:,}")
                
                # File size
                file_size_mb = stats.get('file_size_mb', 0)
                if file_size_mb < 1:
                    size_str = f"{file_size_mb * 1024:.1f} KB"
                else:
                    size_str = f"{file_size_mb:.2f} MB"
                self.recording_filesize_label.setText(f"{t('file_size')}: {size_str}")
    
    def on_save(self):
        """Save settings."""
        self.settings["can_interface"] = self.can_combo.currentText()
        self.settings["simulation_mode"] = self.sim_checkbox.isChecked()
        self.settings["wifi_ssid"] = self.wifi_ssid.text()
        
        # Encrypt and save WiFi password
        from crypto_utils import get_crypto
        wifi_pwd = self.wifi_password.text().strip()
        if wifi_pwd:
            self.settings["wifi_password_encrypted"] = get_crypto().encrypt(wifi_pwd)
        else:
            self.settings["wifi_password_encrypted"] = ""
        
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
        
        # Language Settings
        selected_lang = "DE" if self.language_combo.currentIndex() == 0 else "EN"
        language_changed = self.settings.get("language", "DE") != selected_lang
        self.settings["language"] = selected_lang
        
        # Logging Settings (logging ist immer aktiviert)
        self.settings["logging_enabled"] = True  # Dauerhaft aktiv
        self.settings["logging_interval_sec"] = self.logging_interval_slider.value()
        self.settings["logging_fields"] = [
            field_name for field_name, checkbox in self.field_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        # Trace Replay Settings
        selected_trace_data = self.trace_combo.currentData()
        self.settings["trace_file"] = selected_trace_data if selected_trace_data else ""
        self.settings["trace_loop"] = self.loop_checkbox.isChecked()
        
        self.save_settings()
        
        # Update translator if language changed
        if language_changed:
            self.translator.set_language(selected_lang)
            # Reload UI with new language
            self.reload_ui()
        
        # Apply WLAN Configuration via NetworkManager
        self._apply_wlan_config()
        
        # Show confirmation
        t = self.translator.get
        self.show_message(t("settings_saved"))
    
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
            t = self.translator.get
            self.show_message(t("wlan_timeout"))
        except subprocess.CalledProcessError as e:
            t = self.translator.get
            self.show_message(f"{t('wlan_failed')}:\n{e}")
        except Exception as e:
            t = self.translator.get
            self.show_message(f"{t('wlan_error')}:\n{str(e)}")
    
    def on_cancel(self):
        """Verwerfe Änderungen."""
        t = self.translator.get
        self.settings = self.load_settings()
        self.show_message(t("changes_discarded"))
    
    def on_reboot(self):
        """System neu starten."""
        from PyQt5.QtWidgets import QMessageBox
        t = self.translator.get
        
        reply = QMessageBox.question(
            self, 
            t('reboot'),
            t('reboot_confirm'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.show_message(t("rebooting"))
            from PyQt5.QtCore import QTimer
            import subprocess
            # Warte 2 Sekunden, dann reboot
            QTimer.singleShot(2000, lambda: subprocess.run(['sudo', 'reboot']))
    
    def on_shutdown(self):
        """System herunterfahren."""
        from PyQt5.QtWidgets import QMessageBox
        t = self.translator.get
        
        reply = QMessageBox.question(
            self, 
            t('shutdown'),
            t('shutdown_confirm'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.show_message(t("shutting_down"))
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
    
    def reload_ui(self):
        """Reload UI with new language."""
        # Save current status bar states before reload
        wifi_status = self.status_bar.wifi_connected if hasattr(self, 'status_bar') else False
        replay_status = self.status_bar.replay_active if hasattr(self, 'status_bar') else False
        
        # Clear current layout
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Recreate UI
        self.init_ui()
        
        # Restore status bar states
        if hasattr(self, 'status_bar'):
            self.status_bar.set_wifi_status(wifi_status)
            self.status_bar.set_replay_status(replay_status)
    
    def on_reset_consumption(self):
        """Reset average consumption with confirmation."""
        from PyQt5.QtWidgets import QMessageBox
        t = self.translator.get
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self, 
            t("trip_computer"),
            t("reset_consumption_confirm"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Get trip computer instance from parent (dashboard)
            parent = self.parent()
            if parent and hasattr(parent, 'trip_computer'):
                parent.trip_computer.reset_total_stats()
                self.show_message(t("consumption_reset"))
            else:
                print("Warning: Could not access trip_computer from parent")
    
    def on_reset_soh(self):
        """Reset SOH with confirmation."""
        from PyQt5.QtWidgets import QMessageBox
        t = self.translator.get
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self, 
            t("trip_computer"),
            "SOH auf 100% zurücksetzen?" if t("language") == "DE" else "Reset SOH to 100%?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Get soh_tracker instance from parent (dashboard)
            parent = self.parent()
            if parent and hasattr(parent, 'soh_tracker'):
                parent.soh_tracker.reset_soh(100.0)
                self.show_message("SOH " + ("zurückgesetzt auf 100%" if t("language") == "DE" else "reset to 100%"))
            else:
                print("Warning: Could not access soh_tracker from parent")


# Test-Programm
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    screen = SettingsScreen()
    screen.show()
    sys.exit(app.exec_())
