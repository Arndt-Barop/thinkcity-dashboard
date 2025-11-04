# CAN-Traces

Dieser Ordner enthält aufgezeichnete CAN-Bus Traces für Tests und Simulation.

## Format

Die Traces sind im `candump` Format:

```
(timestamp) can0 CANID#DATA
(1699012345.123456) can0 210#0A1B2C3D4E5F6071
```

## Verwendung

### Trace abspielen

```bash
# Virtual CAN Interface erstellen
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up

# Trace abspielen (50x Geschwindigkeit, Endlos-Loop)
python3 ../tools/can_replay.py entladen_91.log vcan0 50.0 --loop
```

### Eigene Traces aufnehmen

```bash
# CAN-Traffic vom Auto aufzeichnen
candump -l can0

# Erzeugt Datei: candump-2025-11-04_153045.log
# Umbenennen für bessere Übersicht:
mv candump-2025-11-04_153045.log meine_fahrt.log
```

### PCAN-Traces konvertieren

Falls du Traces von PCAN-View (.trc Format) hast:

```bash
python3 ../tools/trc2candump.py input.trc output.log
```

## Trace-Beispiele

- `entladen_91.log` - Komplette Entladefahrt (~48 Min, 860K Frames)
  - Start: SOC ~91%
  - Ende: SOC ~20%
  - Enthält: Beschleunigung, Rekuperation, Konstant

*Weitere Traces sollten NICHT ins Git-Repo (sind zu groß). Stattdessen lokal aufbewahren oder via Download-Link teilen.*

## Trace-Analyse

```bash
# Statistik anzeigen
cantools dump output.log

# Bestimmte CAN-ID filtern
grep " 210#" entladen_91.log | head -20

# Anzahl Frames pro ID
awk '{print $3}' entladen_91.log | cut -d'#' -f1 | sort | uniq -c
```

## Hinweise

- **Dateigröße**: Traces können sehr groß werden (>100 MB für lange Fahrten)
- **Datenschutz**: Traces können GPS-Daten enthalten - nicht öffentlich teilen!
- **Git**: Große Traces gehören in `.gitignore` (siehe ../.gitignore)
