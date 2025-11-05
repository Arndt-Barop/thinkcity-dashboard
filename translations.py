#!/usr/bin/env python3
"""
Translation/Localization system for ThinkCity Dashboard.
Supports German (DE) and English (EN).
"""

TRANSLATIONS = {
    # === Main Screen ===
    "main_screen": {
        "DE": "Hauptansicht",
        "EN": "Main View"
    },
    "speed": {
        "DE": "Geschwindigkeit",
        "EN": "Speed"
    },
    "soc": {
        "DE": "Ladezustand",
        "EN": "State of Charge"
    },
    "range": {
        "DE": "Reichweite",
        "EN": "Range"
    },
    "consumption_now": {
        "DE": "Verbrauch jetzt",
        "EN": "Consumption Now"
    },
    "consumption_avg": {
        "DE": "Ø Verbrauch",
        "EN": "Avg Consumption"
    },
    "power": {
        "DE": "Leistung",
        "EN": "Power"
    },
    "voltage": {
        "DE": "Spannung",
        "EN": "Voltage"
    },
    "current": {
        "DE": "Strom",
        "EN": "Current"
    },
    "pack_temp": {
        "DE": "Akku-Temp",
        "EN": "Pack Temp"
    },
    "ambient_temp": {
        "DE": "Außen-Temp",
        "EN": "Ambient Temp"
    },
    
    # === Status Bar ===
    "can_active": {
        "DE": "CAN",
        "EN": "CAN"
    },
    "wifi_connected": {
        "DE": "WIFI",
        "EN": "WIFI"
    },
    "logging_active": {
        "DE": "LOG",
        "EN": "LOG"
    },
    "simulation_mode": {
        "DE": "DEMO",
        "EN": "DEMO"
    },
    
    # === Trip Computer Screen ===
    "trip_computer": {
        "DE": "Bordcomputer",
        "EN": "Trip Computer"
    },
    "trip_stats": {
        "DE": "Fahrt-Statistik",
        "EN": "Trip Statistics"
    },
    "since_start": {
        "DE": "seit Start",
        "EN": "since start"
    },
    "total_distance": {
        "DE": "Gesamtstrecke",
        "EN": "Total Distance"
    },
    "total_energy": {
        "DE": "Gesamtenergie",
        "EN": "Total Energy"
    },
    "avg_consumption": {
        "DE": "Ø Verbrauch",
        "EN": "Avg Consumption"
    },
    "avg_speed": {
        "DE": "Ø Geschwindigkeit",
        "EN": "Avg Speed"
    },
    "trip_time": {
        "DE": "Fahrtzeit",
        "EN": "Trip Time"
    },
    "battery_info": {
        "DE": "Akku-Information",
        "EN": "Battery Information"
    },
    "capacity_total": {
        "DE": "Kapazität (gesamt)",
        "EN": "Capacity (total)"
    },
    "capacity_remaining": {
        "DE": "Verbleibend",
        "EN": "Remaining"
    },
    "capacity_used": {
        "DE": "Verbraucht",
        "EN": "Used"
    },
    "estimated_range": {
        "DE": "Geschätzte Reichweite",
        "EN": "Estimated Range"
    },
    "at_current": {
        "DE": "bei aktuellem Verbrauch",
        "EN": "at current consumption"
    },
    "reset_trip": {
        "DE": "Fahrt\nzurücksetzen",
        "EN": "Reset\nTrip"
    },
    
    # === Raw Data Screen ===
    "raw_data": {
        "DE": "CAN Rohdaten",
        "EN": "CAN Raw Data"
    },
    "can_terminal": {
        "DE": "CAN Terminal",
        "EN": "CAN Terminal"
    },
    "can_data_table": {
        "DE": "CAN Daten Tabelle",
        "EN": "CAN Data Table"
    },
    "can_id": {
        "DE": "CAN-ID",
        "EN": "CAN-ID"
    },
    "data": {
        "DE": "Daten",
        "EN": "Data"
    },
    "description": {
        "DE": "Beschreibung",
        "EN": "Description"
    },
    
    # === Settings Screen ===
    "settings": {
        "DE": "Einstellungen",
        "EN": "Settings"
    },
    "save": {
        "DE": "Speichern",
        "EN": "Save"
    },
    "cancel": {
        "DE": "Abbrechen",
        "EN": "Cancel"
    },
    "reboot": {
        "DE": "Neu-\nstarten",
        "EN": "Reboot"
    },
    "shutdown": {
        "DE": "Herunter-\nfahren",
        "EN": "Shut-\ndown"
    },
    
    # CAN Interface Settings
    "can_interface": {
        "DE": "CAN-Interface",
        "EN": "CAN Interface"
    },
    "interface": {
        "DE": "Interface",
        "EN": "Interface"
    },
    "simulation_mode_label": {
        "DE": "Simulations-Modus (Demo-Daten)",
        "EN": "Simulation Mode (Demo Data)"
    },
    "simulation_info": {
        "DE": "Info: Im Simulations-Modus werden zufällige Demo-Daten generiert",
        "EN": "Info: Simulation mode generates random demo data"
    },
    
    # Network Settings
    "network_settings": {
        "DE": "Network Settings",
        "EN": "Network Settings"
    },
    "wlan_config": {
        "DE": "WLAN Konfiguration",
        "EN": "WLAN Configuration"
    },
    "ssid": {
        "DE": "SSID",
        "EN": "SSID"
    },
    "ssid_placeholder": {
        "DE": "WLAN Name",
        "EN": "WLAN Name"
    },
    "password": {
        "DE": "Passwort",
        "EN": "Password"
    },
    "password_placeholder": {
        "DE": "WLAN Passwort (wird verschlüsselt)",
        "EN": "WLAN Password (encrypted)"
    },
    "password_info": {
        "DE": "Info: Passwort wird nicht in settings.json gespeichert, nur in NetworkManager",
        "EN": "Info: Password not stored in settings.json, only in NetworkManager"
    },
    "show": {
        "DE": "Show",
        "EN": "Show"
    },
    "hide": {
        "DE": "Hide",
        "EN": "Hide"
    },
    "ip_config": {
        "DE": "IP Konfiguration (nur WLAN)",
        "EN": "IP Configuration (WLAN only)"
    },
    "ip_mode": {
        "DE": "IP-Modus",
        "EN": "IP Mode"
    },
    "dhcp_auto": {
        "DE": "DHCP (automatisch)",
        "EN": "DHCP (automatic)"
    },
    "static_manual": {
        "DE": "Static (manuell)",
        "EN": "Static (manual)"
    },
    "ip_cidr": {
        "DE": "IP/CIDR",
        "EN": "IP/CIDR"
    },
    "ip_placeholder": {
        "DE": "z.B. 192.168.1.100/24",
        "EN": "e.g. 192.168.1.100/24"
    },
    "gateway": {
        "DE": "Gateway",
        "EN": "Gateway"
    },
    "gateway_placeholder": {
        "DE": "z.B. 192.168.1.1",
        "EN": "e.g. 192.168.1.1"
    },
    "dns1": {
        "DE": "DNS 1",
        "EN": "DNS 1"
    },
    "dns1_placeholder": {
        "DE": "z.B. 8.8.8.8",
        "EN": "e.g. 8.8.8.8"
    },
    "dns2": {
        "DE": "DNS 2",
        "EN": "DNS 2"
    },
    "dns2_placeholder": {
        "DE": "z.B. 8.8.4.4 (optional)",
        "EN": "e.g. 8.8.4.4 (optional)"
    },
    "ntp": {
        "DE": "NTP",
        "EN": "NTP"
    },
    "ntp_placeholder": {
        "DE": "z.B. pool.ntp.org (optional)",
        "EN": "e.g. pool.ntp.org (optional)"
    },
    "wlan_status": {
        "DE": "WLAN Status",
        "EN": "WLAN Status"
    },
    "status_loading": {
        "DE": "Status wird beim Öffnen geladen...",
        "EN": "Status loading..."
    },
    "wlan_not_connected": {
        "DE": "[X] WLAN nicht verbunden",
        "EN": "[X] WLAN not connected"
    },
    "wlan_connected": {
        "DE": "[OK] Verbunden mit",
        "EN": "[OK] Connected to"
    },
    "wlan_disconnected": {
        "DE": "[X] WLAN getrennt",
        "EN": "[X] WLAN disconnected"
    },
    "sync_wifi_only": {
        "DE": "NAS-Sync nur bei WLAN-Verbindung",
        "EN": "NAS sync on WLAN only"
    },
    
    # NAS Settings
    "nas_sync": {
        "DE": "NAS Synchronisation",
        "EN": "NAS Synchronization"
    },
    "nas_enable": {
        "DE": "NAS-Sync aktivieren",
        "EN": "Enable NAS sync"
    },
    "nas_host": {
        "DE": "NAS Host/IP",
        "EN": "NAS Host/IP"
    },
    "nas_host_placeholder": {
        "DE": "z.B. 192.168.1.100 oder nas.local",
        "EN": "e.g. 192.168.1.100 or nas.local"
    },
    "nas_path": {
        "DE": "NAS Pfad",
        "EN": "NAS Path"
    },
    "nas_path_placeholder": {
        "DE": "/backup/thinkcity",
        "EN": "/backup/thinkcity"
    },
    "nas_user": {
        "DE": "Benutzer",
        "EN": "User"
    },
    "nas_user_placeholder": {
        "DE": "NAS Benutzername",
        "EN": "NAS Username"
    },
    "nas_password_placeholder": {
        "DE": "NAS Passwort (wird verschlüsselt)",
        "EN": "NAS Password (encrypted)"
    },
    "nas_password_info": {
        "DE": "Info: Passwort wird verschlüsselt in settings.json gespeichert",
        "EN": "Info: Password stored encrypted in settings.json"
    },
    "nas_sync_info": {
        "DE": "Info: Datenbank wird nach jeder Fahrt automatisch synchronisiert",
        "EN": "Info: Database synchronized automatically after each trip"
    },
    
    # Data Logger Settings
    "data_logger": {
        "DE": "Datenlogger",
        "EN": "Data Logger"
    },
    "logging_always_active": {
        "DE": "Info: Daten-Logging ist dauerhaft aktiv",
        "EN": "Info: Data logging is permanently active"
    },
    "db_path": {
        "DE": "Datenbankpfad",
        "EN": "Database Path"
    },
    "db_path_info": {
        "DE": "Info: Standard: /home/pi/thinkcity-dashboard-v3/thinkcity.db",
        "EN": "Info: Default: /home/pi/thinkcity-dashboard-v3/thinkcity.db"
    },
    "log_interval": {
        "DE": "Log-Intervall",
        "EN": "Log Interval"
    },
    "seconds": {
        "DE": "Sekunden",
        "EN": "seconds"
    },
    "interval_info": {
        "DE": "Info: 1s = hohe Genauigkeit, hoher Speicher | 60s = niedrige Genauigkeit, wenig Speicher",
        "EN": "Info: 1s = high accuracy, high storage | 60s = low accuracy, low storage"
    },
    "data_points": {
        "DE": "Zu loggende Datenpunkte",
        "EN": "Data Points to Log"
    },
    "avg_consumption_permanent": {
        "DE": "Ø Durchschnittsverbrauch - Dauerhaft aktiv",
        "EN": "Avg Consumption - Permanently active"
    },
    "select_all": {
        "DE": "Alle",
        "EN": "All"
    },
    "select_none": {
        "DE": "Keine",
        "EN": "None"
    },
    
    # Data field names
    "field_speed": {
        "DE": "Geschwindigkeit",
        "EN": "Speed"
    },
    "field_soc": {
        "DE": "Ladezustand (SOC)",
        "EN": "State of Charge (SOC)"
    },
    "field_voltage": {
        "DE": "Spannung",
        "EN": "Voltage"
    },
    "field_current": {
        "DE": "Strom",
        "EN": "Current"
    },
    "field_power": {
        "DE": "Leistung",
        "EN": "Power"
    },
    "field_pack_temp": {
        "DE": "Akku-Temperatur",
        "EN": "Pack Temperature"
    },
    "field_ambient_temp": {
        "DE": "Außentemperatur",
        "EN": "Ambient Temperature"
    },
    "field_consumption": {
        "DE": "Verbrauch Wh/km",
        "EN": "Consumption Wh/km"
    },
    "field_range": {
        "DE": "Reichweite",
        "EN": "Range"
    },
    "field_odo": {
        "DE": "Kilometerstand",
        "EN": "Odometer"
    },
    "field_latitude": {
        "DE": "GPS Breitengrad",
        "EN": "GPS Latitude"
    },
    "field_longitude": {
        "DE": "GPS Längengrad",
        "EN": "GPS Longitude"
    },
    
    # Language Settings
    "language_settings": {
        "DE": "Sprache / Language",
        "EN": "Language / Sprache"
    },
    "language": {
        "DE": "Sprache",
        "EN": "Language"
    },
    "language_german": {
        "DE": "Deutsch",
        "EN": "German"
    },
    "language_english": {
        "DE": "Englisch",
        "EN": "English"
    },
    
    # Messages
    "settings_saved": {
        "DE": "[OK] Einstellungen gespeichert!\n\nNeustart erforderlich für CAN-Interface Änderung.",
        "EN": "[OK] Settings saved!\n\nRestart required for CAN interface changes."
    },
    "changes_discarded": {
        "DE": "[X] Änderungen verworfen",
        "EN": "[X] Changes discarded"
    },
    "wlan_timeout": {
        "DE": "[!] WLAN-Konfiguration: Zeitüberschreitung",
        "EN": "[!] WLAN configuration: Timeout"
    },
    "wlan_failed": {
        "DE": "[!] WLAN-Konfiguration fehlgeschlagen",
        "EN": "[!] WLAN configuration failed"
    },
    "wlan_error": {
        "DE": "[!] Fehler bei WLAN-Konfiguration",
        "EN": "[!] Error in WLAN configuration"
    },
    "reboot_confirm": {
        "DE": "System wirklich neu starten?",
        "EN": "Really reboot the system?"
    },
    "shutdown_confirm": {
        "DE": "System wirklich herunterfahren?",
        "EN": "Really shutdown the system?"
    },
    "yes": {
        "DE": "Ja",
        "EN": "Yes"
    },
    "no": {
        "DE": "Nein",
        "EN": "No"
    },
    "rebooting": {
        "DE": "System wird neu gestartet...",
        "EN": "System is rebooting..."
    },
    "shutting_down": {
        "DE": "System wird heruntergefahren...",
        "EN": "System is shutting down..."
    },
}


class Translator:
    """Handle translations for the dashboard."""
    
    def __init__(self, language="DE"):
        """Initialize with default language."""
        self.language = language
    
    def set_language(self, language):
        """Change current language."""
        if language in ["DE", "EN"]:
            self.language = language
        else:
            print(f"Warning: Language '{language}' not supported, using 'DE'")
            self.language = "DE"
    
    def get(self, key, fallback=None):
        """Get translation for key in current language."""
        if key in TRANSLATIONS:
            return TRANSLATIONS[key].get(self.language, TRANSLATIONS[key].get("DE", fallback or key))
        return fallback or key
    
    def __call__(self, key, fallback=None):
        """Allow calling translator directly: t('key')"""
        return self.get(key, fallback)


# Global translator instance
_translator = Translator()

def get_translator():
    """Get global translator instance."""
    return _translator

def t(key, fallback=None):
    """Shortcut function for translation."""
    return _translator.get(key, fallback)


if __name__ == "__main__":
    # Test translations
    translator = Translator("DE")
    print("=== Deutsch ===")
    print(f"Main Screen: {translator('main_screen')}")
    print(f"Speed: {translator('speed')}")
    print(f"Settings: {translator('settings')}")
    
    translator.set_language("EN")
    print("\n=== English ===")
    print(f"Main Screen: {translator('main_screen')}")
    print(f"Speed: {translator('speed')}")
    print(f"Settings: {translator('settings')}")
