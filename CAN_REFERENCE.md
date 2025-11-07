# CAN-Bus Message Reference

## Übersicht

**Gesamt: 37 dekodierte CAN-IDs** (Stand: 05.11.2025)

- 10 Basis-IDs (bereits in v1/v2 implementiert)
- 27 erweiterte IDs (neu in v3, aus Traces analysiert)
- **100% Decoder Coverage** - Alle IDs werden erkannt und verarbeitet

---

## Batterie-Management (BMI) - 0x301-0x306

### 0x301 - Haupt-Batteriedaten
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | /10 | A | DC-Strom (signed) |
| 2-3 | /10 | V | DC-Spannung |
| 4-5 | /10 | % | DoD (Depth of Discharge) |
| 6-7 | /10 | °C | Pack-Temperatur |

**Berechnungen:**
- `power_kW = (voltage_V * current_A) / 1000`
- `soc_pct = 100 - dod_pct` (bei Zebra)

**Rate:** ~5 Hz

---

### 0x302 - Fehler & Limits
| Byte | Bit/Faktor | Einheit | Beschreibung |
|------|------------|---------|--------------|
| 0 | Bit 0 | bool | Allgemeiner Fehler |
| 2 | Bit 0 | bool | ISO-Fehler |
| 4-5 | /10 | V | Min Entlade-Spannung |
| 6-7 | /10 | A | Max Entlade-Strom |

**Rate:** ~5 Hz

---

### 0x303 - Lade-/Entlade-Status
| Byte | Bit/Faktor | Beschreibung |
|------|------------|--------------|
| 0-1 | /10 | Max Lade-Strom (A) |
| 2-3 | /10 | Max Lade-Spannung (V) |
| 4 | Bit 0 | Fahrzeug-Laden erlaubt |
| 4 | Bit 1 | Rekuperations-Bremse aktiv |
| 4 | Bit 2 | Entladen erlaubt |
| 4 | Bit 3 | Schnellladen aktiv |
| 4 | Bit 4 | DC/DC-Wandler aktiv |
| 4 | Bit 5 | Klimaanlage an |
| 5 | - | Anzahl freigegebener Batterien |
| 6 | Bit 0 | Reduzierte Batteriezahl |
| 6 | Bit 3 | Notfall |
| 6 | Bit 4 | Crash |
| 6 | Bit 5 | Lüfter-Status |

**Rate:** ~5 Hz

---

### 0x304 - EOC & Temperaturen
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | /10 | V | Max System-Spannung |
| 2 | - | - | System Error Category |
| 3 | Bit 0 | bool | EOC (End of Charge) |
| 3 | Bit 1 | bool | EOC bitte erreichen |
| 3 | Bit 2 | bool | Warte auf OK Temp zum Laden |
| 3 | Bit 3 | bool | Zu viele fehlerhafte Zellen |
| 3 | Bit 4 | bool | AC Heizungs-Relais |
| 3 | Bit 5 | bool | AC Heizungs-Schalter |
| 4-5 | /10 | °C | Temperatur T1 |
| 6-7 | /10 | °C | Temperatur T2 |

**Rate:** ~5 Hz

---

### 0x305 - BMI State & Failed Cells
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | /10 | - | Charger PWM Command |
| 2 | Bits 0-3 | - | BMI State |
| 2 | Bit 4 | bool | Int. ISO-Fehler |
| 2 | Bit 5 | bool | Ext. ISO-Fehler |
| 3 | Bit 0 | bool | Battery Charge Enable |
| 3 | Bit 1 | bool | OCV Messung läuft |
| 3 | Bit 2 | bool | Kein Lade-Strom |
| 3 | Bit 3 | bool | Lade-Überspannung |
| 3 | Bit 4 | bool | Lade-Überstrom |
| 3 | Bits 5-7 | *0.03125 | Batterietyp |
| 4-5 | - | - | Anzahl fehlerhafter Zellen |
| 6 | Bits 1-2 | /2 | BMI Temp-Fehler |
| 6 | Bits 3-4 | *0.125 | Zebra Temp-Fehler |

**Rate:** ~5 Hz

---

### 0x306 - Zusätzliche BMI-Daten
**Status:** Noch zu analysieren (meist 0x00)
**Rate:** ~1 Hz

---

## Vehicle Control Unit (VCU) - 0x250, 0x251, 0x263-0x265, 0x300

### 0x250 - VCU Status 1
| Byte | Beschreibung |
|------|--------------|
| 0 | Status Byte 1 (0xA8 = 168) |
| 1 | Status Byte 2 (0x00) |
| 2 | Status Byte 3 (0x40 = 64) |

**Rate:** ~10 Hz

---

### 0x251 - VCU Status 2
**Status:** Meist 0x00, Funktion unklar
**Rate:** ~10 Hz

---

### 0x263 - General (PCU)
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0 | *2/10 | A | Mains Strom (AC) |
| 1 | - | V | Mains Spannung (AC) |
| 2 | /2 | °C | PCU Umgebungstemperatur |
| 3 | /10 | V | PCU Spannung |
| 5 | /2 | km/h | Geschwindigkeit |

**Rate:** ~2 Hz

---

### 0x264 - Shifter (Gangwahl)
**Hex-Pattern → Gear:**
- `1004011000` = P (Park)
- `1004042100` = R (Reverse)
- `10040104100` = N (Neutral)
- `10040406100` = D (Drive)
- `10041081000` = E (Eco)

**Rate:** ~5 Hz

---

### 0x265 - VCU Counter
| Byte | Faktor | Beschreibung |
|------|--------|--------------|
| 0-1 | - | Counter (meist 0xFFFF) |
| 5 | - | Status (0x5C = 92) |

**Rate:** ~10 Hz

---

### 0x300 - VCU Mode
| Byte | Beschreibung |
|------|--------------|
| 0 | Mode (0x02 = Normal?) |
| 2 | Reserved |

**Rate:** ~1 Hz

---

## Ladegerät (Charger) - 0x310-0x311, 0x352-0x355, 0x359

### 0x310 - Charger Status
| Byte | Beschreibung |
|------|--------------|
| 0 | Status (0x02 = Charging?) |
| 2 | Mode (0x0A = AC?) |

**Rate:** ~5 Hz

---

### 0x311 - Max AC Current
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 1 | *0.2 | A | Max verfügbarer AC-Strom |

**Rate:** ~5 Hz

---

### 0x352 - Charger Setpoints
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0 | Bit 0 | bool | Charger aktiviert |
| 2-3 | /10 | V | Spannungs-Sollwert |
| 4-5 | /10 | A | Strom-Sollwert |

**Beispiel:** `01 01 03 E8 0F 9F` → 100.0V, 399.9A

**Rate:** ~5 Hz

---

### 0x353 - Charger Target
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 1 | - | - | State (0x02 = Active?) |
| 6-7 | /10 | V | Ziel-Spannung |

**Rate:** ~5 Hz

---

### 0x354 - Charger Timer
| Byte | Einheit | Beschreibung |
|------|---------|--------------|
| 1 | h | Timer Stunden |
| 2 | m | Timer Minuten |
| 4-5 | - | Timestamp (unklar) |

**Rate:** ~5 Hz

---

### 0x355 - Charger Active
| Byte | Beschreibung |
|------|--------------|
| 0 | Bit 0 = Charger aktiv |

**Rate:** ~5 Hz

---

### 0x359 - VCU/Charger Command
| Byte | Beschreibung |
|------|--------------|
| 0 | VCU Charger Command |
| 5 | Bit 0 = VCU Ready |

**Rate:** ~5 Hz

---

## Motor/Inverter - 0x3A0-0x3A1

### 0x3A0 - Motor RPM
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 2-3 | ? | RPM | Drehzahl (Scaling TBD) |

**Beispiel:** `00 00 03 90` → 0x0390 = 912

**Rate:** ~2 Hz

---

### 0x3A1 - Motor Torque & Temp
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | ? | Nm | Drehmoment (Scaling TBD) |
| 3 | - | - | Status 1 |
| 4 | - | - | Status 2 |
| 6 | ? | °C | Temperatur (Scaling TBD) |

**Beispiel:** `63 80 00 10 10 00 EB 00` → Torque 0x6380

**Rate:** ~2 Hz

---

## HVAC/Klima - 0x440-0x444

### 0x440 - HVAC Temperaturen
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | ? | °C | Solltemperatur (TBD) |
| 2-3 | ? | °C | Ist-Temperatur (TBD) |

**Beispiel:** `0D 6E 09 0A` → 0x0D6E=3438, 0x090A=2314

**Rate:** ~5 Hz

---

### 0x441-0x443 - HVAC Status 2-4
**Status:** Meist 0x00, Funktion unklar
**Rate:** ~5 Hz

---

### 0x444 - HVAC Mode & Fan
| Byte | Beschreibung |
|------|--------------|
| 0 | Mode (0x31 = 49) |
| 2 | Lüftergeschwindigkeit (0x0A = 10) |

**Rate:** ~5 Hz

---

## EnerDel Batterie - 0x4B0, 0x610-0x611

### 0x4B0 - Module Voltages ✨ NEW!
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | *0.00244140625 | V | Module 1 Voltage |
| 2-3 | *0.00244140625 | V | Module 2 Voltage |
| 4-5 | *0.00244140625 | V | Module 3 Voltage |
| 6-7 | *0.00244140625 | V | Module 4 Voltage |

**Beispiel:** `26 06 26 09 26 01 26 02` → Module 1: 24.414V, Module 2: 24.419V, Module 3: 24.410V, Module 4: 24.410V

**Interpretation:**
- 4 Module à ~24V (jedes Modul = ca. 6 Zellen à 4V)
- Gesamt: ~97.65V (24V × 4)
- Modul-Imbalance zeigt Lade-/Entlade-Probleme

**Rate:** ~5 Hz  
**Implementiert:** Battery Screen (Grün: 24-26V, Gelb: Warnung, Rot: Kritisch)

---

### 0x610 - Zellspannungen & Temperaturen
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | *0.00244140625 | V | Max Zellspannung |
| 2-3 | *0.00244140625 | V | Min Zellspannung |
| 4 | - | °C | Max Pack-Temperatur |
| 5 | - | °C | Min Pack-Temperatur |

**Beispiel:** `06 72 06 6B 0F 0B` → Max: 3.986V, Min: 3.976V, Max Temp: 15°C, Min Temp: 11°C

**Rate:** ~5 Hz

---

### 0x611 - SOC & Cell Average
| Byte | Faktor | Einheit | Beschreibung |
|------|--------|---------|--------------|
| 0-1 | *0.00244140625 | V | Durchschnittliche Zellspannung |
| 2-3 | *0.00244140625 | V | Delta Zellspannung (Max-Min) |
| 4 | *0.4 | % | Cell Voltage SOC |
| 5 | *0.4 | % | Pack SOC (**Hauptwert!**) |
| 6 | *0.4 | % | Pack SOC 1 |
| 7 | *0.4 | % | Pack SOC 2 |

**Wichtig:** Bei EnerDel wird `e_pack_soc_pct` (Byte 5) für SOC verwendet!

**Rate:** ~5 Hz

---

## Diagnose/Part Numbers - 0x30E-0x30F, 0x721-0x723

### 0x30E - Part Number 1 (ASCII)
**Beispiel:** `35 31 35 31 37 34 30 45` = "5151740E"

**Rate:** Selten (~0.03 Hz)

---

### 0x30F - Part Number 2 (ASCII)
**Beispiel:** `30 30 30 30 30 33 34 36` = "00000346"

**Rate:** Selten (~0.03 Hz)

---

### 0x721-0x723 - Diagnose-Daten
**Status:** Noch zu analysieren
**Rate:** ~1 Hz

---

## Zusammenfassung nach Kategorie

| Kategorie | IDs | Anzahl |
|-----------|-----|--------|
| **Batterie (BMI)** | 0x301-0x306 | 6 |
| **Fahrzeug (VCU)** | 0x250-0x251, 0x263-0x265, 0x300 | 6 |
| **Ladegerät** | 0x310-0x311, 0x352-0x355, 0x359 | 7 |
| **Motor/Inverter** | 0x3A0-0x3A1 | 2 |
| **HVAC/Klima** | 0x440-0x444 | 5 |
| **EnerDel** | **0x4B0**, 0x610-0x611 | **3** |
| **Diagnose** | 0x30E-0x30F, 0x721-0x723 | 5 |
| **Unbekannt** | 0x460, 0x495, 0x4CA | 3 |
| **GESAMT** | | **37** |

---

## Testing mit Traces

Die Traces aus `AKKU/191210_PCAN-Traces/` enthalten:

- **191210_Arndt_Think_Laden_ab_91_procent.trc** (33k messages, 240s)
  - Laden von 91% SOC
  - 33 IDs enthalten
  
- **191210_Arndt_Think_Laden_ab_82_procent.trc** (93k messages, 677s)
  - Laden von 82% SOC
  - 33 IDs
  
- **191210_Arndt_Think_Entladen_ab_91_procent.trc** (860k messages, 6152s)
  - Entladen/Fahren ab 91% SOC ✅ **EMPFOHLEN für Tests**
  - **37 IDs** (4 weitere während Fahrt: 0x460, 0x495, 0x4CA, 0x4B0)

**Test-Befehl:**
```bash
python3 test_with_trace.py ../AKKU/191210_PCAN-Traces/191210_Arndt_Think_Laden_ab_91_procent.trc
```

**Ergebnis:** ✅ **100% dekodiert** (860k/860k messages, 37 IDs)

---

## Noch zu klären (TODO)

- [ ] Motor RPM/Torque Scaling-Faktoren
- [ ] HVAC Temperatur Scaling-Faktoren
- [ ] VCU Status-Bytes (0x250, 0xA8/0x40)
- [ ] Diagnose-Messages 0x721-0x723
- [ ] Unbekannte IDs während Fahrt:
  - [ ] 0x460 (155,943 unique patterns, hochdynamisch)
  - [ ] 0x495 (mittlere Variabilität)
  - [ ] 0x4CA (mittlere Variabilität)

**Hinweis:** Unbekannte IDs werden als Placeholder dekodiert (100% Coverage), Daten aber noch nicht interpretiert.

---

**Quelle:** PCAN-Traces vom 10.12.2019, ThinkCity mit EnerDel-Batterie
