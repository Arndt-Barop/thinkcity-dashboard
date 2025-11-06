# can_decoder.py
# Erweiterte Version mit allen CAN-IDs und robuster Fehlerbehandlung
# Basiert auf ENER_AUTORUN.BAS + ThinkCity.dbc

from typing import Dict, Any, Optional
import struct

def _u16(hi: int, lo: int) -> int:
    """Unsigned 16-bit aus zwei Bytes."""
    return (hi << 8) | lo

def _s16(hi: int, lo: int) -> int:
    """Signed 16-bit aus zwei Bytes (Zweierkomplement)."""
    val = (hi << 8) | lo
    if val & 0x8000:
        val = val - 0x10000
    return val

def _safe_get(data: bytes, idx: int, default: int = 0) -> int:
    """Sicherer Byte-Zugriff mit Fallback."""
    try:
        return data[idx] if idx < len(data) else default
    except (IndexError, TypeError):
        return default


class CANDecoder:
    """
    Dekodiert ThinkCity CAN-Frames.
    Unterstützt Zebra- und EnerDel-Batterien.
    """
    
    # CAN-IDs Mapping (Battery Management Interface)
    BMI_1 = 0x301
    BMI_2 = 0x302
    BMI_3 = 0x303
    BMI_4 = 0x304
    BMI_5 = 0x305
    BMI_6 = 0x306  # Additional BMI data
    
    # Vehicle Control Unit
    GENERAL = 0x263
    SHIFTER = 0x264
    VCU_1 = 0x250
    VCU_2 = 0x251
    VCU_3 = 0x265
    VCU_4 = 0x300
    
    # Charger / Power Control
    MAX_AC = 0x311
    CHARGER_1 = 0x310
    CHARGER_2 = 0x352
    CHARGER_3 = 0x353
    CHARGER_4 = 0x354
    CHARGER_5 = 0x355
    CHARGER_6 = 0x359
    
    # Motor / Inverter
    MOTOR_1 = 0x3A0
    MOTOR_2 = 0x3A1
    
    # HVAC / Climate
    HVAC_1 = 0x440
    HVAC_2 = 0x441
    HVAC_3 = 0x442
    HVAC_4 = 0x443
    HVAC_5 = 0x444
    
    # EnerDel Battery
    ENERDEL_1 = 0x610
    ENERDEL_2 = 0x611
    
    # Diagnostics / ID
    DIAG_1 = 0x30E  # Part Numbers (ASCII)
    DIAG_2 = 0x30F  # Part Numbers (ASCII)
    DIAG_3 = 0x721
    DIAG_4 = 0x722
    DIAG_5 = 0x723
    
    def __init__(self):
        self.is_enerdel = False  # Wird bei Empfang von 0x610/0x611 gesetzt
        self.last_values: Dict[int, Dict[str, Any]] = {}
    
    def parse(self, arbid: int, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Dekodiert einen CAN-Frame.
        Gibt dict mit dekodierten Werten zurück oder None bei unbekannter ID.
        """
        # Sichere Byte-Liste mit Padding
        d = [_safe_get(data, i) for i in range(8)]
        
        out: Dict[str, Any] = {"_can_id": arbid}
        
        try:
            # Battery Management Interface
            if arbid == self.BMI_1:
                out.update(self._parse_bmi1(d))
            elif arbid == self.BMI_2:
                out.update(self._parse_bmi2(d))
            elif arbid == self.BMI_3:
                out.update(self._parse_bmi3(d))
            elif arbid == self.BMI_4:
                out.update(self._parse_bmi4(d))
            elif arbid == self.BMI_5:
                out.update(self._parse_bmi5(d))
            elif arbid == self.BMI_6:
                out.update(self._parse_bmi6(d))
            
            # Vehicle Control
            elif arbid == self.GENERAL:
                out.update(self._parse_general(d))
            elif arbid == self.SHIFTER:
                out.update(self._parse_shifter(d))
            elif arbid == self.VCU_1:
                out.update(self._parse_vcu1(d))
            elif arbid == self.VCU_2:
                out.update(self._parse_vcu2(d))
            elif arbid == self.VCU_3:
                out.update(self._parse_vcu3(d))
            elif arbid == self.VCU_4:
                out.update(self._parse_vcu4(d))
            
            # Charger / Power
            elif arbid == self.MAX_AC:
                out.update(self._parse_max_ac(d))
            elif arbid == self.CHARGER_1:
                out.update(self._parse_charger1(d))
            elif arbid == self.CHARGER_2:
                out.update(self._parse_charger2(d))
            elif arbid == self.CHARGER_3:
                out.update(self._parse_charger3(d))
            elif arbid == self.CHARGER_4:
                out.update(self._parse_charger4(d))
            elif arbid == self.CHARGER_5:
                out.update(self._parse_charger5(d))
            elif arbid == self.CHARGER_6:
                out.update(self._parse_charger6(d))
            
            # Motor / Inverter
            elif arbid == self.MOTOR_1:
                out.update(self._parse_motor1(d))
            elif arbid == self.MOTOR_2:
                out.update(self._parse_motor2(d))
            
            # HVAC / Climate
            elif arbid == self.HVAC_1:
                out.update(self._parse_hvac1(d))
            elif arbid == self.HVAC_2:
                out.update(self._parse_hvac2(d))
            elif arbid == self.HVAC_3:
                out.update(self._parse_hvac3(d))
            elif arbid == self.HVAC_4:
                out.update(self._parse_hvac4(d))
            elif arbid == self.HVAC_5:
                out.update(self._parse_hvac5(d))
            
            # EnerDel Battery
            elif arbid == self.ENERDEL_1:
                self.is_enerdel = True
                out.update(self._parse_enerdel1(d))
            elif arbid == self.ENERDEL_2:
                self.is_enerdel = True
                out.update(self._parse_enerdel2(d))
            
            # Diagnostics
            elif arbid == self.DIAG_1:
                out.update(self._parse_diag1(d))
            elif arbid == self.DIAG_2:
                out.update(self._parse_diag2(d))
            elif arbid == self.DIAG_3:
                out.update(self._parse_diag3(d))
            elif arbid == self.DIAG_4:
                out.update(self._parse_diag4(d))
            elif arbid == self.DIAG_5:
                out.update(self._parse_diag5(d))
            
            else:
                return None  # Unbekannte ID
            
            # Cache for diagnostics
            self.last_values[arbid] = out
            
            return out
            
        except Exception as e:
            # Parse error → Log and return None
            print(f"[CAN] Parse error for 0x{arbid:03X}: {e}")
            return None
    
    def _parse_bmi1(self, d: list) -> Dict[str, Any]:
        """0x301: Haupt-Batteriedaten."""
        dccurrent = _s16(d[0], d[1]) / 10.0
        dcvoltage = _u16(d[2], d[3]) / 10.0
        dod = _u16(d[4], d[5]) / 10.0
        temperature = _u16(d[6], d[7]) / 10.0
        dcpower_kw = (dcvoltage * dccurrent) / 1000.0
        
        return {
            "current_A": dccurrent,
            "voltage_V": dcvoltage,
            "dod_pct": dod,
            "pack_temp_C": temperature,
            "power_kW": dcpower_kw,
        }
    
    def _parse_bmi2(self, d: list) -> Dict[str, Any]:
        """0x302: Fehler & Limits."""
        return {
            "err_general": bool(d[0] & 0x01),
            "iso_error": bool(d[2] & 0x01),
            "volts_min_discharge_V": _u16(d[4], d[5]) / 10.0,
            "amps_max_discharge_A": _s16(d[6], d[7]) / 10.0,
        }
    
    def _parse_bmi3(self, d: list) -> Dict[str, Any]:
        """0x303: Lade-/Entlade-Status."""
        return {
            "max_charge_current_A": _s16(d[0], d[1]) / 10.0,
            "max_charge_voltage_V": _u16(d[2], d[3]) / 10.0,
            "vehicle_charge_enabled": bool(d[4] & 0x01),
            "regen_brake_enabled": bool(d[4] & 0x02),
            "discharge_enabled": bool(d[4] & 0x04),
            "fast_charge_enabled": bool(d[4] & 0x08),
            "dc_dc_enabled": bool(d[4] & 0x10),
            "ac_on": bool(d[4] & 0x20),
            "number_released_batteries": d[5],
            "reduced_number_of_batteries": bool(d[6] & 0x01),
            "emergency": bool(d[6] & 0x08),
            "crash": bool(d[6] & 0x10),
            "fan_status": bool(d[6] & 0x20),
            "soc_greater_102": bool(d[6] & 0x40),
            "iso_test_flag": bool(d[6] & 0x80),
            "waiting_temp_err": bool(d[7] & 0x01),
        }
    
    def _parse_bmi4(self, d: list) -> Dict[str, Any]:
        """0x304: EOC & Warnings."""
        return {
            "sys_voltage_max_generator_V": _u16(d[0], d[1]) / 10.0,
            "sys_high_est_err_cat": d[2],
            "sys_eoc": bool(d[3] & 0x01),
            "reach_eoc_please": bool(d[3] & 0x02),
            "waiting_ok_temp_charge": bool(d[3] & 0x04),
            "too_many_failed_cells": bool(d[3] & 0x08),
            "ac_heater_relay_status": bool(d[3] & 0x10),
            "ac_heater_switch_status": bool(d[3] & 0x20),
            "t1_C": _u16(d[4], d[5]) / 10.0,
            "t2_C": _u16(d[6], d[7]) / 10.0,
        }
    
    def _parse_bmi5(self, d: list) -> Dict[str, Any]:
        """0x305: BMI-State & Failed Cells."""
        return {
            "charger_pwm_cmd": _u16(d[0], d[1]) / 10.0,
            "sys_bmi_state": d[2] & 0x0F,
            "sys_int_iso_error": bool(d[2] & 0x10),
            "sys_ext_iso_error": bool(d[2] & 0x20),
            "battery_charge_en": bool(d[3] & 0x01),
            "ocv_meas_in_progress": bool(d[3] & 0x02),
            "no_charge_current": bool(d[3] & 0x04),
            "charge_overvoltage": bool(d[3] & 0x08),
            "charge_overcurrent": bool(d[3] & 0x10),
            "battery_type": (d[3] & 0xE0) * 0.03125,
            "number_of_failed_cells": _u16(d[4], d[5]),
            "sys_bmi_temp_error": (d[6] & 0x06) / 2.0,
            "sys_zebra_temp_error": (d[6] & 0x18) * 0.125,
            "sys_thermal_iso_error": bool(d[6] & 0x20),
            "waiting_ok_temp_discharge": bool(d[6] & 0x40),
        }
    
    def _parse_general(self, d: list) -> Dict[str, Any]:
        """0x263: PCU (Geschwindigkeit, Mains, etc.)."""
        return {
            "pcu_voltage_V": d[3] / 10.0,
            "speed_kmh": d[5] / 2.0,
            "pcu_ambient_temp_C": d[2] / 2.0,
            "mains_voltage_V": d[1],
            "mains_current_A": d[0] * 2.0 / 10.0,
        }
    
    def _parse_shifter(self, d: list) -> Dict[str, Any]:
        """0x264: Gangwahl."""
        hex_str = "".join(f"{b:02X}" for b in d)
        
        # Dekodierung nach Live-Trace-Analyse
        # Format: 01 00 00 4X YY ZZ 00 00
        #                   ^^ ^^ ^^
        # Bytes 3-5 enthalten die Gang-Information
        # Byte 3 variiert zwischen 40 und 41 (vermutlich Status-Flag)
        gear_bytes = f"{d[4]:02X}{d[5]:02X}"
        
        gear_map = {
            "0401": "P",  # Park      
            "0421": "R",  # Reverse   
            "1004": "N",  # Neutral   
            "4006": "D",  # Drive     
            "0081": "E",  # Eco-Mode  (live: 01 00 00 41 00 81 00 00)
            "1008": "E",  # Eco-Mode  (trace: 01 00 00 40 10 08 00 00)
        }
        
        gear = gear_map.get(gear_bytes, "?")
        
        return {
            "shifter_hex": hex_str,
            "gear": gear,
        }
    
    def _parse_max_ac(self, d: list) -> Dict[str, Any]:
        """0x311: Max AC Current."""
        return {
            "max_available_AC_A": d[1] * 0.2,
        }
    
    def _parse_enerdel1(self, d: list) -> Dict[str, Any]:
        """0x610: EnerDel Cell Voltages & Temps."""
        return {
            "is_enerdel": True,
            "e_pack_max_cell_V": _u16(d[0], d[1]) * 0.00244140625,
            "e_pack_min_cell_V": _u16(d[2], d[3]) * 0.00244140625,
            "e_pack_max_temp_C": d[4],
            "e_pack_min_temp_C": d[5],
        }
    
    def _parse_enerdel2(self, d: list) -> Dict[str, Any]:
        """0x611: EnerDel SOC."""
        return {
            "is_enerdel": True,
            "e_pack_avg_cell_V": _u16(d[0], d[1]) * 0.00244140625,
            "e_pack_delta_cell_V": _u16(d[2], d[3]) * 0.00244140625,
            "e_cell_v_soc_pct": d[4] * 0.4,
            "e_pack_soc_pct": d[5] * 0.4,
            "e_pack_soc1_pct": d[6] * 0.4,
            "e_pack_soc2_pct": d[7] * 0.4,
        }
    
    def _parse_bmi6(self, d: list) -> Dict[str, Any]:
        """0x306: Zusätzliche BMI-Daten."""
        return {
            "bmi6_raw": d[:8],  # Noch zu analysieren
        }
    
    def _parse_vcu1(self, d: list) -> Dict[str, Any]:
        """0x250: Vehicle Control Unit 1."""
        return {
            "vcu_status_1": d[0],
            "vcu_status_2": d[1],
            "vcu_status_3": d[2],
        }
    
    def _parse_vcu2(self, d: list) -> Dict[str, Any]:
        """0x251: Vehicle Control Unit 2 (meist 0)."""
        return {
            "vcu2_raw": d[:8],
        }
    
    def _parse_vcu3(self, d: list) -> Dict[str, Any]:
        """0x265: Vehicle Control Unit 3."""
        # Bytes oft: FF FF 00 00 00 5C 00 00
        return {
            "vcu_counter": _u16(d[0], d[1]),
            "vcu_status_byte": d[5],  # 0x5C = 92
        }
    
    def _parse_vcu4(self, d: list) -> Dict[str, Any]:
        """0x300: Vehicle Control Unit 4."""
        return {
            "vcu_mode": d[0],  # 02 = Normal?
            "vcu_reserved": d[2],
        }
    
    def _parse_charger1(self, d: list) -> Dict[str, Any]:
        """0x310: Charger Status 1."""
        # Bytes: 02 00 0A
        return {
            "charger_status": d[0],  # 02 = Charging?
            "charger_mode": d[2],    # 0A = AC?
        }
    
    def _parse_charger2(self, d: list) -> Dict[str, Any]:
        """0x352: Charger Status 2."""
        # Bytes: 01 01 03 E8 0F 9F 00 00
        return {
            "charger_enabled": bool(d[0] & 0x01),
            "charger_voltage_setpoint_V": _u16(d[2], d[3]) / 10.0,
            "charger_current_setpoint_A": _u16(d[4], d[5]) / 10.0,
        }
    
    def _parse_charger3(self, d: list) -> Dict[str, Any]:
        """0x353: Charger Status 3."""
        # Bytes: 01 02 00 04 00 04 0F 51
        return {
            "charger_state": d[1],  # 02 = Active?
            "charger_target_voltage_V": _u16(d[6], d[7]) / 10.0,
        }
    
    def _parse_charger4(self, d: list) -> Dict[str, Any]:
        """0x354: Charger Timing."""
        # Bytes: 01 18 18 00 E3 0B F4 C5
        return {
            "charger_timer_h": d[1],   # 0x18 = 24h
            "charger_timer_m": d[2],   # 0x18 = 24min
            "charger_timestamp": _u16(d[4], d[5]),  # Unbekannt
        }
    
    def _parse_charger5(self, d: list) -> Dict[str, Any]:
        """0x355: Charger Status 5."""
        return {
            "charger_active": bool(d[0] & 0x01),
        }
    
    def _parse_charger6(self, d: list) -> Dict[str, Any]:
        """0x359: Charger/VCU Status."""
        # Bytes: 04 00 00 85 04 01 00 03
        return {
            "vcu_charger_cmd": d[0],
            "vcu_ready": bool(d[5] & 0x01),
        }
    
    def _parse_motor1(self, d: list) -> Dict[str, Any]:
        """0x3A0: Motor/Inverter 1."""
        # Bytes: 00 00 03 90 00 00 00 00
        # 0x0390 = 912 → evtl. RPM?
        rpm_raw = _u16(d[2], d[3])
        return {
            "motor_rpm_raw": rpm_raw,
            "motor_rpm": rpm_raw,  # Scaling noch zu bestimmen
        }
    
    def _parse_motor2(self, d: list) -> Dict[str, Any]:
        """0x3A1: Motor/Inverter 2."""
        # Bytes: 63 80 00 10 10 00 EB 00
        torque_raw = _u16(d[0], d[1])
        return {
            "motor_torque_raw": torque_raw,
            "motor_status_1": d[3],
            "motor_status_2": d[4],
            "motor_temp_C": d[6],  # 0xEB = 235? Scaling unklar
        }
    
    def _parse_hvac1(self, d: list) -> Dict[str, Any]:
        """0x440: HVAC Status 1."""
        # Bytes: 0D 6E 09 0A 00 00 00 00
        temp1 = _u16(d[0], d[1])
        temp2 = _u16(d[2], d[3])
        return {
            "hvac_temp_setpoint_raw": temp1,  # 0x0D6E = 3438
            "hvac_temp_actual_raw": temp2,    # 0x090A = 2314
            # Scaling TBD (maybe /100 for °C?)
        }
    
    def _parse_hvac2(self, d: list) -> Dict[str, Any]:
        """0x441: HVAC Status 2 (meist 0)."""
        return {"hvac2_raw": d[:8]}
    
    def _parse_hvac3(self, d: list) -> Dict[str, Any]:
        """0x442: HVAC Status 3 (meist 0)."""
        return {"hvac3_raw": d[:8]}
    
    def _parse_hvac4(self, d: list) -> Dict[str, Any]:
        """0x443: HVAC Status 4 (meist 0)."""
        return {"hvac4_raw": d[:8]}
    
    def _parse_hvac5(self, d: list) -> Dict[str, Any]:
        """0x444: HVAC Status 5."""
        # Bytes: 31 00 0A 00 00 00 00 00
        return {
            "hvac_mode": d[0],  # 0x31 = 49
            "hvac_fan_speed": d[2],  # 0x0A = 10
        }
    
    def _parse_diag1(self, d: list) -> Dict[str, Any]:
        """0x30E: Diagnose - Part Number 1 (ASCII)."""
        # Bytes: 35 31 35 31 37 34 30 45
        # ASCII: "51517 40E"
        try:
            part_num = ''.join(chr(b) if 32 <= b < 127 else '?' for b in d)
            return {"part_number_1": part_num}
        except:
            return {"part_number_1_raw": d[:8]}
    
    def _parse_diag2(self, d: list) -> Dict[str, Any]:
        """0x30F: Diagnose - Part Number 2 (ASCII)."""
        # Bytes: 30 30 30 30 30 33 34 36
        # ASCII: "00000346"
        try:
            part_num = ''.join(chr(b) if 32 <= b < 127 else '?' for b in d)
            return {"part_number_2": part_num}
        except:
            return {"part_number_2_raw": d[:8]}
    
    def _parse_diag3(self, d: list) -> Dict[str, Any]:
        """0x721: Diagnose 3."""
        return {"diag3_raw": d[:8]}
    
    def _parse_diag4(self, d: list) -> Dict[str, Any]:
        """0x722: Diagnose 4."""
        return {"diag4_raw": d[:8]}
    
    def _parse_diag5(self, d: list) -> Dict[str, Any]:
        """0x723: Diagnose 5."""
        return {"diag5_raw": d[:8]}
    
    def merge_state(self, state: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merged Update in State und berechnet abgeleitete Werte.
        """
        state.update(update)
        
        # SOC: Prefer EnerDel when available
        if "e_pack_soc_pct" in state and state.get("is_enerdel"):
            state["soc_pct"] = max(0.0, min(100.0, float(state["e_pack_soc_pct"])))
        elif "dod_pct" in state:
            state["soc_pct"] = max(0.0, min(100.0, 100.0 - float(state["dod_pct"])))
        
        # Power (falls noch nicht berechnet)
        if "power_kW" not in state and "voltage_V" in state and "current_A" in state:
            state["power_kW"] = (state["voltage_V"] * state["current_A"]) / 1000.0
        
        # SOH estimation (placeholder - later from cell voltages)
        if "soh_pct" not in state:
            state["soh_pct"] = self._estimate_soh(state)
        
        # TEMP: Generiere Test-Zellspannungen falls noch nicht vorhanden
        # (Will be replaced by real decoding later)
        if "cell_voltages" not in state:
            import random
            # Simuliere 88 Zellen mit realistischen Werten um 3.7V
            base_voltage = 3.7
            state["cell_voltages"] = [
                base_voltage + random.uniform(-0.05, 0.05) for _ in range(88)
            ]
        
        return state
    
    def _estimate_soh(self, state: Dict[str, Any]) -> Optional[float]:
        """
        Schätzt SOH aus verfügbaren Daten.
        Vereinfachte Methode - kann später verfeinert werden.
        """
        # Wenn EnerDel: Delta zwischen Max/Min Zellspannung
        if state.get("is_enerdel") and "e_pack_delta_cell_V" in state:
            delta_v = state["e_pack_delta_cell_V"]
            
            # Heuristic: The larger the delta, the worse the SOH
            # Neu: < 0.05V → 100%
            # Alt/Degradiert: > 0.15V → < 80%
            if delta_v < 0.05:
                soh = 100.0
            elif delta_v > 0.15:
                soh = max(70.0, 100.0 - (delta_v - 0.05) * 200.0)
            else:
                soh = 100.0 - (delta_v - 0.05) * 200.0
            
            return max(70.0, min(100.0, soh))
        
        # Fallback: Anzahl fehlerhafter Zellen
        failed_cells = state.get("number_of_failed_cells", 0)
        if failed_cells > 0:
            # Annahme: 96 Zellen total bei EnerDel
            soh = max(70.0, 100.0 - (failed_cells / 96.0) * 30.0)
            return soh
        
        # Keine Daten → Null
        return None
    
    def get_battery_type(self) -> str:
        """Gibt Batterietyp zurück."""
        return "EnerDel" if self.is_enerdel else "Zebra"
