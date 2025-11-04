# raw_data_screen.py
# Live CAN-Bus Rohdaten und ID-Tabelle

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor
from widgets import StatusBar
from collections import deque
from datetime import datetime


class RawDataScreen(QWidget):
    """
    Rohdaten-Bildschirm.
    
    Zeigt:
    - Live CAN-Traffic im Terminal-Stil (obere Hälfte)
    - Tabelle mit bekannten CAN-IDs (untere Hälfte)
    """
    
    # Bekannte CAN-IDs und ihre Bedeutung
    KNOWN_CAN_IDS = {
        0x210: ("Batterie Status 1", "SOC, Spannung, Strom"),
        0x251: ("Batterie Status 2", "Ladezustand, Flags"),
        0x301: ("Batterie Zellen 1-4", "Zellspannungen 1-4"),
        0x302: ("Batterie Zellen 5-8", "Zellspannungen 5-8"),
        0x303: ("Batterie Zellen 9-12", "Zellspannungen 9-12"),
        0x304: ("Batterie Zellen 13-16", "Zellspannungen 13-16"),
        0x305: ("Batterie Zellen 17-20", "Zellspannungen 17-20"),
        0x306: ("Batterie Zellen 21-24", "Zellspannungen 21-24"),
        0x307: ("Batterie Zellen 25-28", "Zellspannungen 25-28"),
        0x308: ("Batterie Zellen 29-32", "Zellspannungen 29-32"),
        0x309: ("Batterie Zellen 33-36", "Zellspannungen 33-36"),
        0x30A: ("Batterie Zellen 37-40", "Zellspannungen 37-40"),
        0x30B: ("Batterie Zellen 41-44", "Zellspannungen 41-44"),
        0x30C: ("Batterie Zellen 45-48", "Zellspannungen 45-48"),
        0x30D: ("Batterie Zellen 49-52", "Zellspannungen 49-52"),
        0x30E: ("Batterie Zellen 53-56", "Zellspannungen 53-56"),
        0x30F: ("Batterie Zellen 57-60", "Zellspannungen 57-60"),
        0x310: ("Batterie Zellen 61-64", "Zellspannungen 61-64"),
        0x311: ("Batterie Zellen 65-68", "Zellspannungen 65-68"),
        0x312: ("Batterie Zellen 69-72", "Zellspannungen 69-72"),
        0x313: ("Batterie Zellen 73-76", "Zellspannungen 73-76"),
        0x314: ("Batterie Zellen 77-80", "Zellspannungen 77-80"),
        0x315: ("Batterie Zellen 81-84", "Zellspannungen 81-84"),
        0x316: ("Batterie Zellen 85-88", "Zellspannungen 85-88"),
        0x4B0: ("Batterie Temperaturen", "Pack/Ambient/Inlet/Outlet Temp"),
        0x495: ("Batterie Limits", "Max Lade-/Entladestrom"),
        0x5E3: ("Motor Status", "Geschwindigkeit, Drehzahl"),
        0x5E5: ("Motor Leistung", "Spannung, Strom, Leistung"),
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.can_buffer = deque(maxlen=500)  # Letzte 500 Frames
        self.last_frames = {}  # {can_id: (timestamp, data, count)}
        self._init_ui()
        
        # Update-Timer für Statistik
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_stats)
        self.update_timer.start(1000)  # Jede Sekunde
    
    def _init_ui(self):
        """Erstellt UI-Layout."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # ====== Status-Bar ======
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # ====== Titel ======
        title = QLabel("CAN-BUS ROHDATEN")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ffcc;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # ====== Splitter (obere/untere Hälfte) ======
        splitter = QSplitter(Qt.Vertical)
        
        # --- Obere Hälfte: Live-Traffic Terminal ---
        terminal_container = QWidget()
        terminal_layout = QVBoxLayout()
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.setSpacing(3)
        
        terminal_title = QLabel("🔴 Live CAN-Traffic")
        terminal_title.setFont(QFont("Arial", 12, QFont.Bold))
        terminal_title.setStyleSheet("color: #00ff00;")
        terminal_layout.addWidget(terminal_title)
        
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Courier", 9))
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00ff00;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """)
        terminal_layout.addWidget(self.terminal)
        
        # Statistik-Zeile
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Frames: 0 | IDs: 0 | Rate: 0.0 fps")
        self.stats_label.setFont(QFont("Arial", 9))
        self.stats_label.setStyleSheet("color: #888888;")
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        
        clear_btn_label = QLabel("💡 Puffer wird automatisch bei 500 Frames geleert")
        clear_btn_label.setFont(QFont("Arial", 9))
        clear_btn_label.setStyleSheet("color: #666666;")
        stats_layout.addWidget(clear_btn_label)
        
        terminal_layout.addLayout(stats_layout)
        
        terminal_container.setLayout(terminal_layout)
        splitter.addWidget(terminal_container)
        
        # --- Untere Hälfte: CAN-ID Tabelle ---
        table_container = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(3)
        
        table_title = QLabel("📋 Bekannte CAN-IDs")
        table_title.setFont(QFont("Arial", 12, QFont.Bold))
        table_title.setStyleSheet("color: #ffaa00;")
        table_layout.addWidget(table_title)
        
        self.id_table = QTableWidget()
        self.id_table.setColumnCount(5)
        self.id_table.setHorizontalHeaderLabels([
            "CAN-ID (Hex)", "CAN-ID (Dez)", "Name", "Inhalt", "Letzte Aktualisierung"
        ])
        self.id_table.setFont(QFont("Arial", 9))
        self.id_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                color: #ffffff;
                border: 2px solid #444444;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #222222;
                color: #00ffcc;
                border: 1px solid #444444;
                padding: 5px;
                font-weight: bold;
            }
        """)
        
        # Auto-resize Spalten
        header = self.id_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Tabelle füllen
        self._populate_id_table()
        
        table_layout.addWidget(self.id_table)
        
        table_container.setLayout(table_layout)
        splitter.addWidget(table_container)
        
        # Splitter-Verhältnis (60% Terminal, 40% Tabelle)
        splitter.setStretchFactor(0, 60)
        splitter.setStretchFactor(1, 40)
        
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
    
    def _populate_id_table(self):
        """Füllt die CAN-ID Tabelle mit bekannten IDs."""
        self.id_table.setRowCount(len(self.KNOWN_CAN_IDS))
        
        for row, (can_id, (name, content)) in enumerate(sorted(self.KNOWN_CAN_IDS.items())):
            # CAN-ID Hex
            hex_item = QTableWidgetItem(f"0x{can_id:03X}")
            hex_item.setFont(QFont("Courier", 9, QFont.Bold))
            hex_item.setForeground(Qt.cyan)
            self.id_table.setItem(row, 0, hex_item)
            
            # CAN-ID Dezimal
            dec_item = QTableWidgetItem(f"{can_id}")
            dec_item.setForeground(Qt.lightGray)
            self.id_table.setItem(row, 1, dec_item)
            
            # Name
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.id_table.setItem(row, 2, name_item)
            
            # Inhalt
            content_item = QTableWidgetItem(content)
            content_item.setForeground(Qt.yellow)
            self.id_table.setItem(row, 3, content_item)
            
            # Letzte Aktualisierung
            time_item = QTableWidgetItem("---")
            time_item.setForeground(Qt.gray)
            self.id_table.setItem(row, 4, time_item)
    
    def add_can_frame(self, can_id, data, timestamp=None):
        """
        Fügt einen CAN-Frame zum Terminal hinzu.
        
        Args:
            can_id: CAN-ID (int)
            data: Daten als bytes oder list
            timestamp: Optional timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # In Buffer speichern
        self.can_buffer.append((timestamp, can_id, data))
        
        # Statistik aktualisieren
        if can_id in self.last_frames:
            ts, old_data, count = self.last_frames[can_id]
            self.last_frames[can_id] = (timestamp, data, count + 1)
        else:
            self.last_frames[can_id] = (timestamp, data, 1)
        
        # Formatiere Daten
        if isinstance(data, bytes):
            data_hex = ' '.join(f'{b:02X}' for b in data)
        elif isinstance(data, list):
            data_hex = ' '.join(f'{b:02X}' for b in data)
        else:
            data_hex = str(data)
        
        # Name nachschlagen
        name = ""
        if can_id in self.KNOWN_CAN_IDS:
            name = f" ({self.KNOWN_CAN_IDS[can_id][0]})"
        
        # Formatierte Zeile
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        line = f"{time_str}  0x{can_id:03X}{name:<30}  [{len(data)}]  {data_hex}\n"
        
        # Zum Terminal hinzufügen
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText(line)
        self.terminal.moveCursor(QTextCursor.End)
        
        # Tabelle aktualisieren (nur für bekannte IDs)
        self._update_id_table_row(can_id, timestamp)
    
    def _update_id_table_row(self, can_id, timestamp):
        """Aktualisiert Zeitstempel in der ID-Tabelle."""
        if can_id not in self.KNOWN_CAN_IDS:
            return
        
        # Finde Row
        for row in range(self.id_table.rowCount()):
            hex_item = self.id_table.item(row, 0)
            if hex_item and hex_item.text() == f"0x{can_id:03X}":
                time_str = timestamp.strftime("%H:%M:%S")
                time_item = QTableWidgetItem(time_str)
                time_item.setForeground(Qt.green)
                self.id_table.setItem(row, 4, time_item)
                break
    
    def _update_stats(self):
        """Aktualisiert Statistik-Anzeige."""
        total_frames = len(self.can_buffer)
        unique_ids = len(self.last_frames)
        
        # Frame-Rate berechnen (Frames der letzten Sekunde)
        now = datetime.now()
        recent_frames = [f for f in self.can_buffer 
                        if (now - f[0]).total_seconds() < 1.0]
        fps = len(recent_frames)
        
        self.stats_label.setText(f"Frames: {total_frames} | IDs: {unique_ids} | Rate: {fps:.1f} fps")
    
    def update(self, state):
        """
        Aktualisiert Screen mit neuem State.
        
        Hinweis: CAN-Frames werden direkt via add_can_frame() hinzugefügt,
        nicht über update(). Diese Methode existiert für Konsistenz.
        """
        # Status-Bar (kompletter State für Fehlerprüfung)
        self.status_bar.set_state(state)
        ambient_temp = state.get("pcu_ambient_temp_C")
        if ambient_temp is not None:
            self.status_bar.set_ambient_temp(ambient_temp)


# Test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    import random
    
    app = QApplication(sys.argv)
    
    screen = RawDataScreen()
    screen.setStyleSheet("background-color: #000000; color: #ffffff;")
    screen.resize(1280, 800)
    
    # Test-Daten generieren
    def generate_test_frames():
        test_ids = [0x210, 0x251, 0x301, 0x4B0, 0x495, 0x5E3]
        can_id = random.choice(test_ids)
        data = bytes([random.randint(0, 255) for _ in range(8)])
        screen.add_can_frame(can_id, data)
    
    # Timer für Test-Frames
    test_timer = QTimer()
    test_timer.timeout.connect(generate_test_frames)
    test_timer.start(100)  # 10 fps
    
    screen.show()
    sys.exit(app.exec_())
