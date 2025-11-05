# widgets.py
# Wiederverwendbare UI-Widgets für ThinkCity Dashboard

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QPoint, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QLinearGradient
import math


class PowerGauge(QWidget):
    """
    Halbkreis-Anzeige für Leistung mit pseudo-logarithmischer Skalierung.
    Bereich: -50 kW (Rekuperation) bis +200 kW (Vollgas)
    Grün = Rekuperation, Gelb = Fahren, Rot = Vollgas
    
    Skalierung:
    - -50 bis 0 kW: Linear (25% des Bogens)
    - 0 bis +30 kW: Linear (40% des Bogens) - wichtigster Bereich
    - +30 bis +200 kW: Komprimiert (35% des Bogens)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.power_kw = 0.0
        self.min_power = -50.0
        self.max_power = 200.0
        self.setMinimumSize(300, 180)
    
    def set_power(self, power_kw: float):
        """Setzt Leistungswert und triggert Redraw."""
        self.power_kw = max(self.min_power, min(self.max_power, power_kw))
        self.update()
    
    def _power_to_angle_pct(self, power: float) -> float:
        """
        Konvertiert Leistung zu Winkel-Prozent (0.0 - 1.0) mit pseudo-log Skalierung.
        
        Bereiche:
        - -50 bis 0 kW   → 0% bis 25% (linear)
        - 0 bis +30 kW   → 25% bis 65% (linear)
        - +30 bis +200 kW → 65% bis 100% (komprimiert)
        """
        if power <= 0:
            # Rekuperation: -50 kW = 0%, 0 kW = 25%
            return 0.25 * (power + 50.0) / 50.0
        elif power <= 30:
            # Normal: 0 kW = 25%, 30 kW = 65%
            return 0.25 + 0.40 * (power / 30.0)
        else:
            # Vollgas: 30 kW = 65%, 200 kW = 100%
            return 0.65 + 0.35 * ((power - 30.0) / 170.0)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hintergrund
        painter.fillRect(self.rect(), QColor(20, 20, 20))
        
        # Dimensionen
        w = self.width()
        h = self.height()
        center = QPoint(w // 2, h - 20)
        radius = min(w, h * 2) // 2 - 40
        
        rect = QRect(center.x() - radius, center.y() - radius,
                     radius * 2, radius * 2)
        
        # Farbige Segmente zeichnen (statisch)
        self._draw_colored_segments(painter, rect, center, radius)
        
        # Skala-Striche mit Beschriftung zeichnen
        self._draw_scale(painter, center, radius, w, h)
        
        # Zeiger-Position berechnen
        power_pct = self._power_to_angle_pct(self.power_kw)
        angle_deg = 180.0 * power_pct
        needle_angle = math.radians(180 - angle_deg)
        needle_length = radius - 15
        needle_end = QPoint(
            center.x() + int(needle_length * math.cos(needle_angle)),
            center.y() - int(needle_length * math.sin(needle_angle))
        )
        
        # Zeiger-Linie (weiß, deutlich sichtbar)
        pen = QPen(Qt.white, 4, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(center, needle_end)
        
        # Zentrum-Punkt (weiß)
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawEllipse(center, 10, 10)
        
        # Text: Leistungswert (rechts neben dem Instrument)
        painter.setPen(Qt.white)
        font = QFont("Arial", 36, QFont.Bold)
        painter.setFont(font)
        
        text = f"{self.power_kw:+.0f}"
        text_rect = QRect(w - 180, center.y() - 60, 160, 60)
        painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, text)
        
        # Einheit "kW" kleiner darunter
        font_unit = QFont("Arial", 18)
        painter.setFont(font_unit)
        painter.setPen(QColor(150, 150, 150))
        unit_rect = QRect(w - 180, center.y(), 160, 30)
        painter.drawText(unit_rect, Qt.AlignRight | Qt.AlignVCenter, "kW")
    
    
    def _draw_colored_segments(self, painter, rect, center, radius):
        """Zeichnet statische farbige Segmente auf der Skala."""
        # Segmente definieren:
        # -50 bis -5 kW: Grün (starke Rekuperation) - LINKS
        # -5 bis 0 kW: Hellgrün (leichte Rekuperation)
        # 0 bis 15 kW: Gelb (normale Fahrt)
        # 15 bis 50 kW: Orange (sportlich)
        # 50 bis 200 kW: Rot (Vollgas) - RECHTS
        
        segments = [
            (-50, -5, QColor(0, 255, 100)),      # Grün (links)
            (-5, 0, QColor(100, 255, 150)),      # Hellgrün
            (0, 15, QColor(255, 220, 0)),        # Gelb (mitte)
            (15, 50, QColor(255, 140, 0)),       # Orange
            (50, 200, QColor(255, 50, 50))       # Rot (rechts)
        ]
        
        for start_power, end_power, color in segments:
            start_pct = self._power_to_angle_pct(start_power)
            end_pct = self._power_to_angle_pct(end_power)
            
            # Qt Winkel: 0° = rechts (3 Uhr), gegen Uhrzeigersinn
            # Für Halbkreis von links nach rechts: Start bei 180° (links)
            # Unser start_pct: 0.0 = links (-50kW), 1.0 = rechts (+200kW)
            # Qt Winkel: 180° = links, 0° = rechts
            start_angle_qt = int((1.0 - end_pct) * 180 * 16)  # Invertiert!
            span_angle = int((end_pct - start_pct) * 180 * 16)
            
            pen = QPen(color, 12, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, start_angle_qt, span_angle)
    
    def _draw_scale(self, painter, center, radius, w, h):
        """Zeichnet Skala-Striche und Zahlenbeschriftung."""
        # Skala-Werte: -50, -25, 0, 10, 20, 30, 50, 100, 150, 200
        scale_values = [-50, -25, 0, 10, 20, 30, 50, 100, 150, 200]
        
        painter.setPen(QColor(150, 150, 150))
        font_scale = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font_scale)
        
        for value in scale_values:
            # Winkel für diesen Wert berechnen
            angle_pct = self._power_to_angle_pct(value)
            angle_rad = math.radians(180 - (180.0 * angle_pct))
            
            # Strich-Positionen
            tick_start = radius - 20
            tick_end = radius - 5
            
            x_start = center.x() + int(tick_start * math.cos(angle_rad))
            y_start = center.y() - int(tick_start * math.sin(angle_rad))
            x_end = center.x() + int(tick_end * math.cos(angle_rad))
            y_end = center.y() - int(tick_end * math.sin(angle_rad))
            
            # Strich zeichnen (dicker für 0, 50, 100, 200)
            if value in [0, 50, 100, 200]:
                pen = QPen(QColor(200, 200, 200), 3)
            else:
                pen = QPen(QColor(120, 120, 120), 2)
            painter.setPen(pen)
            painter.drawLine(x_start, y_start, x_end, y_end)
            
            # Text-Position (etwas weiter außen)
            text_dist = radius + 15
            x_text = center.x() + int(text_dist * math.cos(angle_rad))
            y_text = center.y() - int(text_dist * math.sin(angle_rad))
            
            # Text zeichnen
            painter.setPen(QColor(180, 180, 180))
            if value == 0:
                text = "0"
            elif value > 0:
                text = f"+{value}"
            else:
                text = str(value)
            
            # Text-Rechteck zentriert um Position
            text_rect = QRect(x_text - 25, y_text - 10, 50, 20)
            painter.drawText(text_rect, Qt.AlignCenter, text)


class DigitalDisplay(QWidget):
    """
    Digital-Anzeige für Werte mit Einheit.
    Groß und Touch-freundlich.
    """
    
    def __init__(self, label: str, unit: str, parent=None):
        super().__init__(parent)
        self.label = label
        self.unit = unit
        self.value = 0.0
        self.decimals = 1
        self.color = QColor(0, 255, 200)  # Cyan
        self.setMinimumSize(140, 100)
    
    def set_value(self, value: float):
        """Setzt Wert und triggert Redraw."""
        self.value = value
        self.update()
    
    def set_color(self, color: QColor):
        """Setzt Farbe der Anzeige."""
        self.color = color
        self.update()
    
    def set_decimals(self, decimals: int):
        """Setzt Anzahl Dezimalstellen."""
        self.decimals = decimals
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hintergrund: Leichter Gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(30, 30, 30))
        gradient.setColorAt(1, QColor(20, 20, 20))
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Border
        pen = QPen(QColor(60, 60, 60), 2)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        w = self.width()
        h = self.height()
        
        # Label (klein, oben)
        font_label = QFont("Arial", 11)
        painter.setFont(font_label)
        painter.setPen(QColor(150, 150, 150))
        label_rect = QRect(0, 10, w, 20)
        painter.drawText(label_rect, Qt.AlignCenter, self.label)
        
        # Wert (groß, Mitte)
        font_value = QFont("Arial", 32, QFont.Bold)
        painter.setFont(font_value)
        painter.setPen(self.color)
        
        value_text = f"{self.value:.{self.decimals}f}"
        value_rect = QRect(0, 30, w, 45)
        painter.drawText(value_rect, Qt.AlignCenter, value_text)
        
        # Einheit (mittel, unten)
        font_unit = QFont("Arial", 14)
        painter.setFont(font_unit)
        painter.setPen(QColor(150, 150, 150))
        unit_rect = QRect(0, h - 30, w, 20)
        painter.drawText(unit_rect, Qt.AlignCenter, self.unit)


class StatusBar(QWidget):
    """
    Status-Leiste oben auf allen Screens: Datum, Uhrzeit, Außentemperatur.
    Zeigt kritische Warnungen mit roter Umrandung und Icon.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ambient_temp = None
        self.state = {}  # Speichert aktuellen State für Fehlerprüfung
        self.wifi_connected = False  # WLAN-Status
        self.simulation_active = False  # Simulation-Status
        self.setFixedHeight(30)  # Schmaler!
        self.setMinimumWidth(400)
    
    def set_ambient_temp(self, temp_c: float):
        """Setzt Außentemperatur."""
        self.ambient_temp = temp_c
        self.update()
    
    def set_state(self, state: dict):
        """Setzt kompletten State für Fehlerprüfung."""
        self.state = state
        self.update()
    
    def set_wifi_status(self, connected: bool):
        """Setzt WLAN-Verbindungsstatus."""
        self.wifi_connected = connected
        self.update()
    
    def set_simulation_status(self, active: bool):
        """Setzt Simulation-Status."""
        self.simulation_active = active
        self.update()
    
    def _get_critical_warning(self):
        """
        Prüft State auf kritische Fehler und gibt Warnung zurück.
        
        Returns:
            tuple: (warning_text, icon) oder (None, None) wenn alles OK
        """
        # Priorisierte Fehlerprüfung (schwerste zuerst)
        
        # 1. Isolationsfehler (höchste Priorität)
        if self.state.get("iso_error"):
            return ("⚠ ISOLATION", "⚠")
        
        # 2. Emergency/Notfall
        if self.state.get("emergency"):
            return ("⚠ NOTFALL", "⚠")
        
        # 3. Zellspannungs-Fehler
        cell_voltages = self.state.get("cell_voltages", [])
        if cell_voltages:
            valid_voltages = [v for v in cell_voltages if v is not None and v > 0]
            if valid_voltages:
                max_v = max(valid_voltages)
                min_v = min(valid_voltages)
                
                if max_v > 4.25:  # Überladen (kritisch!)
                    return ("⚡ ÜBERLADEN", "⚡")
                elif min_v < 2.5:  # Tiefentladen (kritisch!)
                    return ("🔋 TIEFENTLADEN", "🔋")
        
        # 4. Temperatur-Fehler
        pack_temp = self.state.get("pack_temp_C")
        if pack_temp is not None:
            if pack_temp > 55:
                return ("🌡 TEMP HOCH", "🌡")
            elif pack_temp < -10:
                return ("❄ TEMP TIEF", "❄")
        
        # 5. Weitere BMS-Fehler
        if self.state.get("waiting_temp_err"):
            return ("⚠ TEMP-ERR", "⚠")
        
        # Alles OK
        return (None, None)
    
    def paintEvent(self, event):
        from datetime import datetime
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Kritische Warnung prüfen
        warning_text, warning_icon = self._get_critical_warning()
        has_warning = warning_text is not None
        
        # Hintergrund (rot bei Warnung!)
        if has_warning:
            painter.fillRect(self.rect(), QColor(80, 20, 20, 230))  # Dunkles Rot
            # Rote Umrandung (dick und auffällig)
            painter.setPen(QPen(QColor(255, 50, 50), 3))
            painter.drawRect(self.rect().adjusted(1, 1, -2, -2))
        else:
            painter.fillRect(self.rect(), QColor(30, 30, 30, 200))
        
        # Aktuelle Zeit
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M:%S")
        
        # LINKS: Datum
        font_date = QFont("Arial", 11)
        painter.setFont(font_date)
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(10, 0, 100, h, Qt.AlignLeft | Qt.AlignVCenter, date_str)
        
        # LINKS-MITTE: Warnung (wenn vorhanden)
        if has_warning:
            painter.setPen(QColor(255, 255, 255))
            font_warning = QFont("Arial", 11, QFont.Bold)
            painter.setFont(font_warning)
            # Blinkendes Icon (nur Text, keine echten Icons in Qt ohne Bilder)
            import time
            blink = int(time.time() * 2) % 2 == 0  # 2x pro Sekunde
            if blink:
                painter.drawText(120, 0, 180, h, Qt.AlignLeft | Qt.AlignVCenter, warning_text)
        
        # MITTE: Uhrzeit
        if not has_warning:
            painter.setPen(QColor(200, 200, 200))
        else:
            painter.setPen(QColor(255, 255, 255))  # Weiß bei Warnung
        font_time = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font_time)
        painter.drawText(0, 0, w, h, Qt.AlignCenter, time_str)
        
        # RECHTS-MITTE: Status-Icons (WLAN, Simulation)
        icon_x = w - 240  # Startposition für Icons
        font_icon = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font_icon)
        
        # WLAN-Icon (wenn verbunden)
        if self.wifi_connected:
            painter.setPen(QColor(0, 255, 100))  # Grün
            painter.drawText(icon_x, 0, 50, h, Qt.AlignCenter, "[WiFi]")
            icon_x += 55
        
        # Simulation-Icon (wenn aktiv)
        if self.simulation_active:
            painter.setPen(QColor(255, 200, 0))  # Gelb
            painter.drawText(icon_x, 0, 50, h, Qt.AlignCenter, "[SIM]")
            icon_x += 55
        
        # RECHTS: Außentemperatur (wenn vorhanden)
        if self.ambient_temp is not None:
            temp_str = f"{self.ambient_temp:.1f}°C"
            
            # Frostwarnung: Rot bei unter 3°C
            if self.ambient_temp < 3.0:
                temp_color = QColor(255, 80, 80)  # Rot (Frost!)
                painter.setPen(temp_color)
                font_temp = QFont("Arial", 14, QFont.Bold)  # Fett bei Warnung
            else:
                temp_color = QColor(100, 200, 255)  # Hellblau (normal)
                painter.setPen(temp_color)
                font_temp = QFont("Arial", 12, QFont.Bold)
            
            painter.setFont(font_temp)
            painter.drawText(w - 110, 0, 100, h, Qt.AlignRight | Qt.AlignVCenter, temp_str)


class GearDisplay(QWidget):
    """
    Großes Fahrmodus-Display (P/N/R/D/E).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gear = "P"
        self.setMinimumSize(80, 100)
    
    def set_gear(self, gear: str):
        """Setzt Fahrmodus."""
        self.gear = gear if gear else "?"
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hintergrund
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        # Rahmen
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        w = self.width()
        h = self.height()
        
        # Farbe je nach Gang
        if self.gear == "R":
            color = QColor(255, 100, 100)  # Rot für Rückwärts
        elif self.gear == "P":
            color = QColor(200, 200, 200)  # Grau für Park
        elif self.gear == "E":
            color = QColor(100, 255, 100)  # Grün für Eco
        else:
            color = QColor(0, 255, 200)    # Cyan für N/D
        
        # Fahrmodus-Text
        painter.setPen(color)
        font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, w, h, Qt.AlignCenter, self.gear)
        
        # Label "Gang" klein darunter
        painter.setPen(QColor(120, 120, 120))
        font_label = QFont("Arial", 10)
        painter.setFont(font_label)
        painter.drawText(0, h - 15, w, 12, Qt.AlignCenter, "GANG")


class BatteryBar(QWidget):
    """
    Horizontale Batterie-Balken-Anzeige mit SOC-Prozent.
    Farbe ändert sich: Grün > Gelb > Orange > Rot
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.soc_pct = 100.0
        self.setMinimumSize(300, 60)
    
    def set_soc(self, soc_pct: float):
        """Setzt SOC-Wert (0-100%)."""
        self.soc_pct = max(0.0, min(100.0, soc_pct))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hintergrund
        painter.fillRect(self.rect(), QColor(20, 20, 20))
        
        w = self.width()
        h = self.height()
        
        # Batterie-Rahmen
        margin = 10
        bar_rect = QRectF(margin, margin, w - 2 * margin - 20, h - 2 * margin)
        pole_rect = QRectF(w - margin - 15, h // 2 - 10, 15, 20)
        
        # Rahmen zeichnen
        painter.setPen(QPen(QColor(100, 100, 100), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(bar_rect, 5, 5)
        painter.drawRoundedRect(pole_rect, 3, 3)
        
        # Füllfarbe basierend auf SOC
        if self.soc_pct > 60:
            fill_color = QColor(0, 255, 100)  # Grün
        elif self.soc_pct > 30:
            fill_color = QColor(255, 220, 0)  # Gelb
        elif self.soc_pct > 15:
            fill_color = QColor(255, 140, 0)  # Orange
        else:
            fill_color = QColor(255, 50, 50)  # Rot
        
        # Füllung zeichnen
        fill_width = (bar_rect.width() - 4) * (self.soc_pct / 100.0)
        fill_rect = QRectF(
            bar_rect.left() + 2,
            bar_rect.top() + 2,
            fill_width,
            bar_rect.height() - 4
        )
        
        gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomLeft())
        gradient.setColorAt(0, fill_color.lighter(120))
        gradient.setColorAt(1, fill_color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(fill_rect, 3, 3)
        
        # SOC-Text
        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.white)
        
        text = f"{self.soc_pct:.0f}%"
        painter.drawText(bar_rect, Qt.AlignCenter, text)


class TouchButton(QWidget):
    """
    Touch-freundlicher Button mit Custom Styling.
    Größere Version für bessere Bedienbarkeit.
    """
    
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text
        self.pressed = False
        self.setMinimumSize(140, 70)  # Größer für Touch
        self.callback = None
    
    def set_callback(self, callback):
        """Setzt Click-Callback."""
        self.callback = callback
    
    def setText(self, text: str):
        """Ändert den Button-Text."""
        self.text = text
        self.update()
    
    def mousePressEvent(self, event):
        self.pressed = True
        self.update()
    
    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.update()
        
        # Trigger Callback
        if self.callback and self.rect().contains(event.pos()):
            self.callback()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Farbe basierend auf State
        if self.pressed:
            bg_color = QColor(0, 120, 255)
        else:
            bg_color = QColor(60, 60, 60)
        
        # Gradient-Hintergrund
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, bg_color.lighter(130))
        gradient.setColorAt(1, bg_color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 8, 8)
        
        # Text (größer)
        font = QFont("Arial", 16, QFont.Bold)  # Größere Schrift
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)


# Test-Code
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout
    import sys
    
    app = QApplication(sys.argv)
    
    # Test-Fenster
    window = QWidget()
    window.setWindowTitle("Widget Tests")
    window.resize(800, 600)
    window.setStyleSheet("background-color: #1a1a1a;")
    
    layout = QVBoxLayout()
    
    # Power Gauge
    gauge = PowerGauge()
    gauge.set_power(-12.5)
    layout.addWidget(gauge)
    
    # Digital Displays
    row1 = QHBoxLayout()
    speed_display = DigitalDisplay("Geschwindigkeit", "km/h")
    speed_display.set_value(67.5)
    row1.addWidget(speed_display)
    
    range_display = DigitalDisplay("Reichweite", "km")
    range_display.set_value(112.0)
    range_display.set_color(QColor(255, 200, 0))
    row1.addWidget(range_display)
    
    consumption = DigitalDisplay("Verbrauch", "kWh/100km")
    consumption.set_value(15.8)
    consumption.set_color(QColor(255, 100, 100))
    row1.addWidget(consumption)
    
    layout.addLayout(row1)
    
    # Battery Bar
    battery = BatteryBar()
    battery.set_soc(67.0)
    layout.addWidget(battery)
    
    # Buttons
    row2 = QHBoxLayout()
    btn1 = TouchButton("Hauptansicht")
    btn2 = TouchButton("Batterie")
    btn3 = TouchButton("Laden")
    row2.addWidget(btn1)
    row2.addWidget(btn2)
    row2.addWidget(btn3)
    layout.addLayout(row2)
    
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec_())
