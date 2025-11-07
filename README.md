# ThinkCity Dashboard v3

**Modern PyQt5 Dashboard for Think City Electric Vehicles**

**Raspberry Pi 4B + HDMI Touchscreen + MCP2515 CAN**

A complete CAN bus dashboard for Raspberry Pi with SunFounder 10" HDMI touchscreen and MCP2515 CAN interface. Developed with Claude Sonnet 3.5 for precise CAN bus decoding and professional UI design.

[🇩🇪 Deutsche Version](README_DE.md)

## ⚠️ Disclaimer

**This project is not affiliated with or authorized by Think Global AS, Electric Mobility Solutions AS, or any manufacturer of the Think City vehicle.** "Think City" refers solely to the electric vehicle model. This dashboard was developed as a community project for Think City vehicle owners.

---

## 📸 Screenshots

### Main Screen
![Main Screen](docs/images/screen1-main.png)
*Speed, Power Gauge (-50 to +200 kW), Range, Consumption, Drive Mode*

### Battery Overview
![Battery Screen](docs/images/screen2-battery.png)
*Voltages, Currents, Temperatures, SOC, SOH, Status Flags*

### Cell Voltages
![Cell Voltages Screen](docs/images/screen3-cells.png)
*All 88 cells individually with bar graphs and color coding*

### Charging Status
![Charge Screen](docs/images/screen4-charge.png)
*AC/DC values, charging current, estimated charging time*

### CAN Raw Data
![Raw Data Screen](docs/images/screen5-rawdata.png)
*Live CAN traffic with ID reference table*

---

![Dashboard Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204B-red)

---

## ✨ Features

### 📊 **5 Main Screens**

- **Main**: Speed, Power Gauge, Range, Consumption, Drive Mode (P/N/R/D/E)
- **Battery**: Voltages, Currents, Temperatures, Status Flags, **Module Voltages (4 modules)**
- **Cells**: Detailed view of all 88 cell voltages with bar graphs
- **Charge**: Charging status, AC/DC values, time estimates
- **Raw Data**: Live CAN terminal + ID reference table
- **Settings**: System configuration, CAN interface, Network, Logging, **Trace Replay**

### 🎛️ **Power Gauge with Logarithmic Scaling**

- Range: -50 kW (Recuperation) to +200 kW (Full Power)
- Pseudo-logarithmic scaling for better resolution in normal range (0-30 kW)
- Static color segments: Green (Recuperation) → Yellow → Orange → Red (Full Power)

### 🌍 **Bilingual UI (DE/EN)**

- Complete translation system with 150+ UI strings
- Language switcher in Settings screen
- Instant UI reload when language changes

### 🎨 **Professional UI Design**

- Touch-optimized buttons (minimum 80px height)
- Modern flat design with clear color coding
- Status bar on all screens with date, time, ambient temperature
- **Frost warning**: Ambient temperature <3°C highlighted in red

### 🚨 **Intelligent Warning System**

Critical battery conditions trigger visual warnings:
- Cell undervoltage (<3.0V)
- Cell overvoltage (>4.15V)
- High temperature (>45°C)
- Low temperature (<5°C)
- Isolation error (⚠ ISOLATION)
- Contactor error (⚠ CONTACTOR)

### 🔋 **Cell Voltage Monitoring**

- All 88 cells displayed individually (4 rows × 22 cells)
- Color-coded bar graphs:
  - Red: <3.0V or >4.15V (critical)
  - Orange: <3.0V (critically low)
  - Green: 3.5-4.1V (optimal)
  - Yellow: Borderline range
- Thick red border for critical cells
- Min/Max/Average/Delta display

### 📡 **Robust CAN Bus Integration**

- Reliable initialization with retry logic
- Automatic recovery from CAN bus errors
- Complete decoding of all known ThinkCity CAN IDs (37 unique IDs, 100% coverage)
- **Module Voltage Monitoring**: 4 battery modules individually displayed (0x4B0)
- PCAN trace replay for development/testing (vcan0)
- Start/Pause/Stop controls for trace playback

### 💾 **Data Logging & Performance**

- SQLite database on SSD with auto-mount check
- Trip tracking (start/stop detection)
- Selective UI update (only changed values)
- Optimized rendering for low CPU usage

---

## 📦 Installation

### Prerequisites

**Hardware:**
- Raspberry Pi 4B
- USB SSD (recommended for fast boot)
- HDMI touchscreen (tested with SunFounder 10" 1280x800)
- MCP2515 CAN module (SPI interface)

**Software:**
- Raspberry Pi OS Lite (64-bit recommended)
- Python 3.9+
- PyQt5, python-can, SQLite3

### Quick Start

```bash
git clone https://github.com/Arndt-Barop/thinkcity-dashboard.git
cd thinkcity-dashboard-v3
chmod +x setup.sh
sudo ./setup.sh
```

The setup script will:
1. Install all dependencies
2. Configure CAN interface (MCP2515)
3. Set up systemd services
4. Configure touchscreen calibration
5. Enable auto-start on boot

See [INSTALL.md](INSTALL.md) for detailed manual installation steps.

---

## 🖥️ Hardware Requirements

### Minimum
- Raspberry Pi 4B with 2GB RAM
- 16GB microSD card (USB boot recommended for speed)
- 5V/2.5A USB-C power supply
- 7" HDMI touchscreen (min. 800x480)

### Recommended
- Raspberry Pi 4B with 4GB RAM
- USB SSD (128GB+) for database and fast boot
- High-quality 5V/3A USB-C power supply
- 10" HDMI touchscreen (1280x800)
- MCP2515 CAN module with 8MHz crystal

### CAN Bus Connection

Connect MCP2515 to Raspberry Pi SPI:

```
MCP2515    Raspberry Pi
-------    ------------
VCC    →   Pin 2  (5V)
GND    →   Pin 6  (GND)
CS     →   Pin 24 (CE0)
SO     →   Pin 21 (MISO)
SI     →   Pin 19 (MOSI)
SCK    →   Pin 23 (SCLK)
INT    →   Pin 22 (GPIO25)
```

Connect CAN-H and CAN-L to vehicle OBD port.

---

## 🎮 Operation

### Touch Navigation

- **Touch buttons** at bottom: Switch between 5 main screens
- **Settings button** (⚙️): System configuration
- **Swipe gestures**: Not implemented (button-based navigation)

### Keyboard Shortcuts (Debug)

- `Q`: Quit application
- `F`: Toggle fullscreen
- `R`: Reset trip computer
- `1-5`: Switch to screen 1-5

---

## 📊 Calculated Values

### Range (km)

```
Range = (SOC / 100) × Battery_Capacity_kWh × 1000 / Average_Consumption_Wh_km
```

**Parameters:**
- **Battery Capacity:** 24 kWh (EnerDel), calibratable in Settings
- **Average Consumption:** Calculated from last 100 samples (rolling window)

### Instantaneous Consumption (Wh/km)

```
Instant_Consumption = (Power_kW / Speed_km_h) × 1000
```

**Only calculated when speed > 2 km/h**

### Trip Computer

- Automatically detects trip start/stop (ignition key state)
- Tracks total distance, total energy, average consumption
- Persisted in database (survives hard shutdown)
- Manual reset via Settings menu

---

## 🛠️ Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- CAN Trace Replay setup (vcan0)
- NAS synchronization
- Database schema
- Custom modifications

### Development Setup

```bash
# Clone repository
git clone https://github.com/Arndt-Barop/thinkcity-dashboard.git
cd thinkcity-dashboard-v3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run dashboard with vcan0 (no hardware needed)
python3 dashboard.py
```

See [INSTALL.md](INSTALL.md) for full installation guide.

---

## 📁 Project Structure

```
thinkcity-dashboard-v3/
├── dashboard.py                # Main application
├── main_screen.py              # Main screen
├── battery_screen.py           # Battery overview
├── cells_screen.py             # Cell voltages
├── charge_screen.py            # Charging status
├── raw_screen.py               # CAN raw data
├── settings_screen.py          # Settings menu
├── widgets.py                  # Custom widgets
├── translations.py             # Translation system
├── db_manager.py               # Database interface
├── trip_computer.py            # Trip calculations
├── trace_parser.py             # PCAN trace parser
├── trace_player.py             # CAN trace replay
├── test_trace_replay.py        # Trace replay tests
├── can_decoder.py              # CAN message decoder
├── crypto_utils.py             # Password encryption
├── requirements.txt            # Python dependencies
├── config.json                 # User settings
├── thinkcity.db                # SQLite database
├── traces/                     # PCAN trace files (.trc)
├── systemd/                    # Service files
│   ├── thinkcity-dashboard.service
│   ├── can-interface.service
│   └── can-trace-replay.service
├── docs/                       # Documentation
│   └── images/                 # Screenshots
└── tools/                      # Utilities
    └── setup_vcan0.sh          # Virtual CAN setup
```

---

## 🔧 Troubleshooting

### Dashboard Won't Start

```bash
# Check service status
systemctl status thinkcity-dashboard

# View logs
journalctl -u thinkcity-dashboard -f

# Test CAN interface
candump can0
```

### CAN Bus Errors

```bash
# Restart CAN interface
sudo systemctl restart can-interface

# Check kernel messages
dmesg | grep -i spi
dmesg | grep -i mcp
```

### Touch Not Working

```bash
# Install touchscreen tools
sudo apt install xinput-calibrator

# Calibrate touchscreen
DISPLAY=:0 xinput_calibrator
```

### Database Issues

```bash
# Check database integrity
sqlite3 thinkcity.db "PRAGMA integrity_check;"

# Backup database
cp thinkcity.db thinkcity.db.backup

# Reset database (creates new schema)
rm thinkcity.db
python3 dashboard.py
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 👨‍💻 Credits

- **Development:** Arndt Barop + Claude Sonnet 3.5
- **CAN Database:** Community reverse engineering
- **Testing:** Think City owners community

## 📧 Contact

For questions, issues, or suggestions:
- GitHub Issues: [thinkcity-dashboard/issues](https://github.com/Arndt-Barop/thinkcity-dashboard/issues)
- Email: [your-email@example.com]

---

**⚡ Built with ❤️ for the Think City Community**
