#!/usr/bin/env python3
"""
nas_sync.py
Synchronisiert die SQLite-Datenbank zum NAS wenn WLAN verfügbar ist.
"""

import os
import sys
import json
import time
import subprocess
import socket
from datetime import datetime

CONFIG_FILE = os.path.expanduser("~/thinkcity-dashboard-v3/config.json")
LOG_FILE = os.path.expanduser("~/thinkcity-dashboard-v3/nas_sync.log")

def log(message):
    """Schreibe Log-Nachricht."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_msg + '\n')
    except:
        pass

def load_config():
    """Lade Konfiguration."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"Config load error: {e}")
        return None

def check_wifi(ssid):
    """Prüfe ob mit spezifischem WLAN verbunden."""
    try:
        result = subprocess.run(
            ['iwgetid', '-r'],
            capture_output=True,
            text=True,
            timeout=5
        )
        current_ssid = result.stdout.strip()
        log(f"Current SSID: {current_ssid}")
        return current_ssid == ssid
    except Exception as e:
        log(f"WiFi check error: {e}")
        return False

def check_nas_reachable(host, timeout=5):
    """Prüfe ob NAS erreichbar ist."""
    try:
        # Versuche CIFS-Port 445
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, 445))
        sock.close()
        
        if result == 0:
            log(f"NAS {host} is reachable on port 445")
            return True
        
        # Fallback: Ping
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(timeout), host],
            capture_output=True,
            timeout=timeout + 1
        )
        reachable = result.returncode == 0
        log(f"NAS {host} ping: {'success' if reachable else 'failed'}")
        return reachable
        
    except Exception as e:
        log(f"NAS reachability check error: {e}")
        return False

def sync_database(config):
    """Synchronisiere Datenbank via rsync."""
    db_path = config.get('db_path', '/home/pi/thinkcity-dashboard-v3/thinkcity.db')
    nas_host = config['nas_host']
    nas_path = config['nas_path']
    nas_user = config.get('nas_user', 'pi')
    
    # Erstelle Backup-Dateiname mit Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    remote_file = f"{nas_user}@{nas_host}:{nas_path}/thinkcity_{timestamp}.db"
    
    try:
        # rsync mit SSH (oder SMB/CIFS wenn mount)
        log(f"Syncing {db_path} to {remote_file}...")
        
        # Option 1: rsync via SSH
        cmd = [
            'rsync',
            '-avz',
            '--timeout=30',
            db_path,
            remote_file
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log(f"✅ Sync successful: {remote_file}")
            
            # Behalte nur die letzten 10 Backups
            cleanup_old_backups(config)
            return True
        else:
            log(f"❌ Sync failed: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"❌ Sync error: {e}")
        return False

def cleanup_old_backups(config, keep=10):
    """Lösche alte Backups, behalte nur die neuesten."""
    try:
        nas_host = config['nas_host']
        nas_path = config['nas_path']
        nas_user = config.get('nas_user', 'pi')
        
        # Liste alle Backups
        cmd = [
            'ssh',
            f"{nas_user}@{nas_host}",
            f"ls -t {nas_path}/thinkcity_*.db"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            
            # Delete old (keep newest 'keep')
            if len(files) > keep:
                to_delete = files[keep:]
                for file in to_delete:
                    delete_cmd = ['ssh', f"{nas_user}@{nas_host}", f"rm {file}"]
                    subprocess.run(delete_cmd, timeout=10)
                    log(f"🗑️ Deleted old backup: {file}")
        
    except Exception as e:
        log(f"Cleanup error: {e}")

def main():
    """Hauptfunktion."""
    log("=== NAS Sync gestartet ===")
    
    # Lade Config
    config = load_config()
    if not config:
        log("❌ Keine Konfiguration gefunden")
        return 1
    
    # Check if sync enabled
    if not config.get('nas_sync_enabled', False):
        log("ℹ️ NAS Sync ist deaktiviert")
        return 0
    
    # Check WLAN (optional)
    if config.get('sync_on_wifi_only', True):
        wifi_ssid = config.get('wifi_ssid', '')
        if not wifi_ssid:
            log("⚠️ Kein WLAN SSID konfiguriert")
            return 1
        
        if not check_wifi(wifi_ssid):
            log(f"ℹ️ Nicht mit {wifi_ssid} verbunden, überspringe Sync")
            return 0
    
    # Check NAS reachability
    nas_host = config.get('nas_host', '')
    if not nas_host:
        log("❌ Kein NAS Host konfiguriert")
        return 1
    
    if not check_nas_reachable(nas_host):
        log(f"❌ NAS {nas_host} nicht erreichbar")
        return 1
    
    # Sync
    success = sync_database(config)
    
    log("=== NAS Sync beendet ===")
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
