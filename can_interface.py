# can_interface.py
# Robuste CAN-Interface-Initialisierung mit Retry-Logik

import can
import time
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CANInterface:
    """
    CAN-Interface-Manager mit automatischer Reconnect-Logik.
    """
    
    def __init__(
        self,
        channel: str = "vcan0",
        bustype: str = "socketcan",
        bitrate: int = 500000,
        retry_interval: float = 5.0,
        max_retries: int = 10
    ):
        self.channel = channel
        self.bustype = bustype
        self.bitrate = bitrate
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.bus: Optional[can.BusABC] = None
    
    def connect(self) -> bool:
        """
        Verbindet zum CAN-Bus mit Retry-Logik.
        Gibt True bei Erfolg zurück.
        """
        retries = 0
        
        while retries < self.max_retries:
            try:
                # Check if interface exists
                if not self._check_interface_exists():
                    logger.warning(
                        f"CAN interface {self.channel} not found, "
                        f"retrying in {self.retry_interval}s..."
                    )
                    time.sleep(self.retry_interval)
                    retries += 1
                    continue
                
                # Erstelle Bus-Instanz
                self.bus = can.interface.Bus(
                    channel=self.channel,
                    bustype=self.bustype,
                    bitrate=self.bitrate
                )
                
                logger.info(f"Connected to {self.channel} @ {self.bitrate} bps")
                return True
                
            except can.CanError as e:
                logger.error(f"CAN error: {e}, retry {retries+1}/{self.max_retries}")
                retries += 1
                time.sleep(self.retry_interval)
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                retries += 1
                time.sleep(self.retry_interval)
        
        logger.critical(f"Failed to connect to {self.channel} after {self.max_retries} retries")
        return False
    
    def _check_interface_exists(self) -> bool:
        """Prüft ob CAN-Interface im System vorhanden ist."""
        net_path = f"/sys/class/net/{self.channel}"
        return os.path.exists(net_path)
    
    def receive(self, timeout: float = 1.0) -> Optional[can.Message]:
        """
        Empfängt eine CAN-Nachricht.
        Gibt None zurück bei Timeout oder Fehler.
        """
        if not self.bus:
            logger.error("Bus not connected")
            return None
        
        try:
            msg = self.bus.recv(timeout=timeout)
            return msg
        
        except can.CanError as e:
            logger.error(f"Receive error: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected receive error: {e}")
            return None
    
    def send(self, arbid: int, data: bytes) -> bool:
        """
        Sendet eine CAN-Nachricht.
        Gibt True bei Erfolg zurück.
        """
        if not self.bus:
            logger.error("Bus not connected")
            return False
        
        try:
            msg = can.Message(
                arbitration_id=arbid,
                data=data,
                is_extended_id=False
            )
            self.bus.send(msg)
            return True
        
        except can.CanError as e:
            logger.error(f"Send error: {e}")
            return False
        
        except Exception as e:
            logger.error(f"Unexpected send error: {e}")
            return False
    
    def shutdown(self):
        """Schließt die CAN-Bus-Verbindung."""
        if self.bus:
            logger.info(f"Shutting down {self.channel}")
            self.bus.shutdown()
            self.bus = None
    
    def reconnect(self) -> bool:
        """Führt Reconnect durch (shutdown + connect)."""
        logger.info("Attempting reconnect...")
        self.shutdown()
        time.sleep(1.0)
        return self.connect()


def setup_can_interface(channel: str = "vcan0", bitrate: int = 500000) -> bool:
    """
    Hilfsfunktion zur manuellen Interface-Konfiguration via ip link.
    Nützlich wenn kein systemd-Service läuft.
    """
    import subprocess
    
    try:
        # Interface down
        subprocess.run(
            ["sudo", "ip", "link", "set", channel, "down"],
            check=False, capture_output=True
        )
        
        # Setze Bitrate
        subprocess.run(
            ["sudo", "ip", "link", "set", channel, "type", "can", "bitrate", str(bitrate)],
            check=True, capture_output=True
        )
        
        # Interface up
        subprocess.run(
            ["sudo", "ip", "link", "set", channel, "up"],
            check=True, capture_output=True
        )
        
        logger.info(f"CAN interface {channel} configured @ {bitrate} bps")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to setup CAN interface: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error during CAN setup: {e}")
        return False


# CLI Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing CAN interface...")
    
    # Setup (if needed)
    setup_can_interface()
    
    # Connect
    can_if = CANInterface()
    if not can_if.connect():
        print("ERROR: Could not connect to CAN bus")
        exit(1)
    
    print("Listening for CAN messages (Ctrl+C to stop)...")
    
    try:
        while True:
            msg = can_if.receive(timeout=1.0)
            if msg:
                print(f"  0x{msg.arbitration_id:03X}: {msg.data.hex()}")
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        can_if.shutdown()
