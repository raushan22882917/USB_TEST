# USB Device Manager API

Simple REST API for managing USB serial devices and reading sensor data. Perfect for mobile app integration.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install fastapi uvicorn pyserial
```

### 2. Start the API Server
```bash
python3 usb_api.py
```

### 3. API will be available at:
- **Local**: http://localhost:8000
- **Network**: http://YOUR_PI_IP:8000

## 📱 4 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check API status |
| `/devices` | GET | List USB devices |
| `/connect` | POST | Connect to device |
| `/data` | GET | Get sensor data |

## 🔌 Supported Devices

- **CP2102 USB to UART Bridge Controller** (Silicon Labs)
- Any USB serial device with JSON data output

## 📊 Sensor Data Format

```json
{
  "soc": 85.3,
  "battery_i": 12.4,
  "battery_v": 390.2,
  "temp": 32.6,
  "rpm": 1500
}
```

## 📱 Mobile App Integration

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete mobile app integration examples.

### Quick Test:
```bash
# Check health
curl http://localhost:8000/health

# List devices
curl http://localhost:8000/devices

# Connect to device
curl -X POST http://localhost:8000/connect \
  -H "Content-Type: application/json" \
  -d '{"device_path": "/dev/cu.usbserial-0001", "baudrate": 115200}'

# Get data
curl http://localhost:8000/data
```

## 🌐 Network Setup for Raspberry Pi

1. **Find Pi IP:**
   ```bash
   hostname -I
   ```

2. **Update mobile app API_BASE:**
   ```javascript
   const API_BASE = 'http://192.168.1.100:8000'; // Your Pi's IP
   ```

3. **Ensure same network** - Pi and mobile device must be on same WiFi

## 📋 Features

- ✅ **Real-time sensor data** reading
- ✅ **Device auto-detection** and listing
- ✅ **Mobile-friendly** REST API
- ✅ **Raw data logging** to terminal
- ✅ **Cross-platform** support (Linux, macOS, Windows)
- ✅ **No authentication** required for simple setup

## 🛠️ Development

- **Raw data** is printed to terminal when reading from USB device
- **No file output** - keeps system clean
- **Auto-reload** enabled for development
- **CORS enabled** for web/mobile access

## 📚 Documentation

- [Complete API Documentation](API_DOCUMENTATION.md) - Detailed mobile app integration guide
- [Advanced USB Monitor](advanced_usb_monitor.py) - Standalone monitoring tool

---

**Ready for mobile app integration!** 🎯