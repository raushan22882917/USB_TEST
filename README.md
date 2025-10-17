# 🚀 Universal USB Device API

A powerful REST API that works with **ANY USB device** - automatically detects, connects, and reads data from USB devices. Perfect for IoT projects, sensor monitoring, and hardware integration.

## 🌐 **Live Demo**

**🔗 Deployed API**: [https://usb-test.onrender.com](https://usb-test.onrender.com)

**📚 API Documentation**: [https://usb-test.onrender.com/docs](https://usb-test.onrender.com/docs)

---

## ✨ **Features**

- 🔌 **Universal USB Support** - Works with ANY USB device (Arduino, ESP32, sensors, etc.)
- 🤖 **Auto-Detection** - Automatically detects device type and optimal settings
- 📊 **Multi-Format Data** - Supports JSON, CSV, text, and binary data
- 🌍 **Cross-Platform** - Works on Windows, Linux, macOS
- ☁️ **Cloud Ready** - Deploy anywhere with cloud device simulation
- 🔄 **Real-time Data** - Live sensor data streaming
- 📱 **Frontend Ready** - RESTful API perfect for web/mobile apps

---

## 🚀 **Quick Start**

### **1. USB Device Insertion Flow**

```bash
# 1. Insert your USB device (Arduino, ESP32, CP2102, etc.)

# 2. Auto-detect and connect
curl -X POST https://usb-test.onrender.com/usb-inserted

# 3. Read data from connected device
curl https://usb-test.onrender.com/data

# 4. Disconnect when done
curl -X POST https://usb-test.onrender.com/disconnect
```

### **2. Frontend Integration Example**

```javascript
// Auto-connect to USB device
const connectDevice = async () => {
  const response = await fetch('https://usb-test.onrender.com/usb-inserted', {
    method: 'POST'
  });
  const result = await response.json();
  console.log('Connected to:', result.device.description);
  return result;
};

// Read sensor data
const readData = async () => {
  const response = await fetch('https://usb-test.onrender.com/data');
  const data = await response.json();
  console.log('Temperature:', data.temp, '°C');
  console.log('Humidity:', data.sensor_data.humidity, '%');
  return data;
};
```

---

## 📋 **Complete API Endpoints**

### **🔍 Device Detection & Connection**

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/devices` | List all USB devices | [Try it](https://usb-test.onrender.com/devices) |
| `GET` | `/auto-detect` | Auto-detect and connect to best device | [Try it](https://usb-test.onrender.com/auto-detect) |
| `POST` | `/usb-inserted` | **🎯 Handle USB insertion - Auto-connect** | [Try it](https://usb-test.onrender.com/usb-inserted) |
| `GET` | `/monitor-usb` | Monitor for new USB devices | [Try it](https://usb-test.onrender.com/monitor-usb) |
| `POST` | `/connect` | Manual device connection | [Try it](https://usb-test.onrender.com/connect) |
| `POST` | `/disconnect` | Disconnect from device | [Try it](https://usb-test.onrender.com/disconnect) |

### **📊 Data Reading**

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/data` | **🎯 Read data from connected device** | `?data_format=auto` |

### **🔧 System Info**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and endpoints |
| `GET` | `/health` | Health check and connection status |
| `GET` | `/docs` | Interactive API documentation |

---

## 🎯 **USB Insertion Flow (Recommended)**

### **Step 1: Insert USB Device**
```bash
# Plug in your USB device (Arduino, ESP32, CP2102, sensor, etc.)
```

### **Step 2: Auto-Connect**
```bash
curl -X POST https://usb-test.onrender.com/usb-inserted
```

**Response:**
```json
{
  "status": "connected",
  "message": "Successfully connected to USB device: CP2102 USB to UART Bridge Controller",
  "device": {
    "path": "/dev/cloud/cp2102",
    "description": "CP2102 USB to UART Bridge Controller",
    "manufacturer": "Silicon Labs",
    "vid": 4292,
    "pid": 60000,
    "baudrate": 115200
  },
  "next_steps": {
    "get_data": "/data",
    "health_check": "/health",
    "disconnect": "/disconnect"
  }
}
```

### **Step 3: Read Data**
```bash
curl https://usb-test.onrender.com/data
```

**Response:**
```json
{
  "timestamp": "2025-10-17T08:39:58.377767",
  "data_size": 206,
  "raw_data": "{\"temperature\": 24.58, \"humidity\": 65.15}",
  "formatted_data": {
    "temperature": 24.58,
    "humidity": 65.15,
    "pressure": 988.98,
    "battery_voltage": 3.91,
    "signal_strength": -44
  },
  "sensor_data": {
    "temperature": 24.58,
    "humidity": 65.15,
    "pressure": 988.98
  },
  "temp": 24.58,
  "battery_v": 3.91
}
```

### **Step 4: Disconnect**
```bash
curl -X POST https://usb-test.onrender.com/disconnect
```

---

## 🌍 **Environment Support**

### **Local Development**
- ✅ **Real USB Devices** - Detects actual hardware
- ✅ **Physical Connection** - Connects to real devices
- ✅ **Live Data** - Reads real sensor data

### **Cloud Deployment**
- ✅ **Simulated Devices** - Cloud-compatible device simulation
- ✅ **Mock Data** - Realistic sensor data generation
- ✅ **Same API** - Identical endpoints and responses

---

## 🔧 **Supported Devices**

| Device Type | Examples | Auto-Detection | Baudrate |
|-------------|----------|----------------|----------|
| **Arduino** | Uno, Nano, Mega | ✅ | 115200 |
| **ESP32** | ESP32, ESP8266 | ✅ | 115200 |
| **USB-Serial** | CP2102, FTDI | ✅ | 115200 |
| **Sensors** | Temperature, Humidity | ✅ | 9600 |
| **GPS** | NMEA GPS modules | ✅ | 9600 |
| **Generic** | Any USB device | ✅ | Auto-detect |

---

## 📱 **Frontend Integration Examples**

### **React/JavaScript**
```javascript
class USBDeviceManager {
  constructor() {
    this.apiUrl = 'https://usb-test.onrender.com';
  }

  async insertUSB() {
    const response = await fetch(`${this.apiUrl}/usb-inserted`, {
      method: 'POST'
    });
    return await response.json();
  }

  async readSensorData() {
    const response = await fetch(`${this.apiUrl}/data`);
    return await response.json();
  }

  async disconnect() {
    const response = await fetch(`${this.apiUrl}/disconnect`, {
      method: 'POST'
    });
    return await response.json();
  }
}

// Usage
const usbManager = new USBDeviceManager();

// Insert USB device
const connection = await usbManager.insertUSB();
console.log('Connected to:', connection.device.description);

// Read data every second
setInterval(async () => {
  const data = await usbManager.readSensorData();
  updateUI(data);
}, 1000);
```

### **Python**
```python
import requests

API_URL = "https://usb-test.onrender.com"

# Insert USB device
response = requests.post(f"{API_URL}/usb-inserted")
connection = response.json()
print(f"Connected to: {connection['device']['description']}")

# Read sensor data
data_response = requests.get(f"{API_URL}/data")
sensor_data = data_response.json()
print(f"Temperature: {sensor_data['temp']}°C")
print(f"Humidity: {sensor_data['sensor_data']['humidity']}%")

# Disconnect
requests.post(f"{API_URL}/disconnect")
```

### **cURL Commands**
```bash
# Complete USB workflow
curl -X POST https://usb-test.onrender.com/usb-inserted
curl https://usb-test.onrender.com/data
curl -X POST https://usb-test.onrender.com/disconnect
```

---

## 🔍 **API Response Examples**

### **Device List**
```json
[
  {
    "device": "/dev/cloud/cp2102",
    "description": "CP2102 USB to UART Bridge Controller",
    "manufacturer": "Silicon Labs",
    "vid": 4292,
    "pid": 60000,
    "serial_number": "CLOUD001",
    "device_type": "generic",
    "recommended_baudrate": 115200,
    "supported_formats": ["json", "text", "csv", "binary"]
  }
]
```

### **Health Check**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T08:39:32.580194",
  "api_version": "2.0.0",
  "device_connected": true,
  "connected_device": "/dev/cloud/cp2102",
  "platform": "Linux"
}
```

---

## 🚀 **Local Development**

### **Prerequisites**
- Python 3.8+
- pip
- USB device (optional for testing)

### **Installation**
```bash
# Clone repository
git clone <your-repo-url>
cd usb_test

# Create virtual environment
python -m venv usb_env
source usb_env/bin/activate  # On Windows: usb_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python start_server.py
```

### **Local API**
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Real USB devices detected automatically**

---

## 📊 **Data Formats Supported**

| Format | Description | Example |
|--------|-------------|---------|
| **JSON** | Structured data | `{"temp": 24.5, "humidity": 65}` |
| **CSV** | Comma-separated | `temperature,humidity\n24.5,65` |
| **Text** | Plain text | `Temp: 24.5C, Humidity: 65%` |
| **Binary** | Raw bytes | `0x48 0x65 0x6C 0x6C 0x6F` |

---

## 🔧 **Advanced Usage**

### **Manual Device Connection**
```bash
curl -X POST https://usb-test.onrender.com/connect \
  -H "Content-Type: application/json" \
  -d '{
    "device_path": "/dev/cloud/cp2102",
    "baudrate": 115200,
    "data_format": "json"
  }'
```

### **Data Format Specification**
```bash
# Get data in specific format
curl "https://usb-test.onrender.com/data?data_format=json"
curl "https://usb-test.onrender.com/data?data_format=csv"
curl "https://usb-test.onrender.com/data?data_format=text"
```

### **Continuous Monitoring**
```javascript
// Monitor for new USB devices
const monitorUSB = async () => {
  const response = await fetch('https://usb-test.onrender.com/monitor-usb');
  const status = await response.json();
  
  if (status.auto_connected) {
    console.log('New device connected:', status.connected_device);
    startDataCollection();
  }
};

// Check every 5 seconds
setInterval(monitorUSB, 5000);
```

---

## 🛠️ **Troubleshooting**

### **Common Issues**

| Issue | Solution |
|-------|----------|
| No devices detected | Check USB connection, try `/monitor-usb` |
| Connection failed | Verify device compatibility, try different baudrate |
| No data available | Ensure device is sending data, check data format |
| API not responding | Check internet connection, verify API URL |

### **Error Responses**
```json
{
  "detail": "No device connected. Use /auto-detect or /connect first."
}
```

---

## 📞 **Support & Documentation**

- **🔗 Live API**: [https://usb-test.onrender.com](https://usb-test.onrender.com)
- **📚 Interactive Docs**: [https://usb-test.onrender.com/docs](https://usb-test.onrender.com/docs)
- **📋 Complete API Docs**: See `COMPLETE_API_DOCUMENTATION.md`

---

## 🎯 **Perfect For**

- 🔬 **IoT Projects** - Sensor data collection
- 📱 **Mobile Apps** - Hardware integration
- 🌐 **Web Applications** - Real-time device monitoring
- 🤖 **Automation** - Device control and monitoring
- 📊 **Data Logging** - Continuous sensor data collection
- 🎓 **Education** - Learning hardware programming

---

## ⚡ **Quick Test**

Try the complete workflow right now:

```bash
# 1. Check API status
curl https://usb-test.onrender.com/health

# 2. Auto-connect to USB device
curl -X POST https://usb-test.onrender.com/usb-inserted

# 3. Read sensor data
curl https://usb-test.onrender.com/data

# 4. Disconnect
curl -X POST https://usb-test.onrender.com/disconnect
```

**🚀 Your USB device is now integrated with your frontend application!**