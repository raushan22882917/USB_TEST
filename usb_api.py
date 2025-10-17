#!/usr/bin/env python3
"""
Universal USB Device Monitoring REST API
Works with ANY USB device - automatically detects and connects
Supports multiple data formats: JSON, CSV, Binary, Text
"""

# Import serial with cloud fallback
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    serial = None
    serial.tools = None
import json
import time
import logging
import re
import csv
import io
from datetime import datetime
import threading
from typing import List, Dict, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Query
try:
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
except ImportError:
    # Fallback for import issues
    CORSMiddleware = None
    StaticFiles = None
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
import platform
import os

# Configure logging
handlers = [logging.StreamHandler(), logging.FileHandler('usb_api.log')]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# Global variables for USB monitoring
usb_monitor = None

class USBDeviceInfo(BaseModel):
    """Universal USB Device Information Model"""
    device: str
    description: str
    manufacturer: Optional[str] = None
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    hwid: Optional[str] = None
    is_connected: bool = False
    device_type: Optional[str] = None
    recommended_baudrate: Optional[int] = None
    supported_formats: List[str] = []

class USBDataResponse(BaseModel):
    """Universal USB Data Response Model"""
    timestamp: str
    data_size: int
    raw_data: str
    formatted_data: Optional[Dict[str, Any]] = None
    data_type: str = "unknown"
    device_info: Optional[Dict[str, Any]] = None
    
    # Common sensor data fields (auto-detected)
    sensor_data: Optional[Dict[str, Union[str, int, float]]] = None
    
    # Legacy fields for backward compatibility
    soc: Optional[float] = None
    battery_i: Optional[float] = None
    battery_v: Optional[float] = None
    temp: Optional[float] = None
    rpm: Optional[float] = None

class ConnectionRequest(BaseModel):
    """Universal Connection Request Model"""
    device_path: Optional[str] = None
    baudrate: Optional[int] = None
    auto_detect: bool = True
    data_format: str = "auto"  # auto, json, csv, text, binary
    timeout: int = 5

class DeviceDetectionResponse(BaseModel):
    """Device Detection Response"""
    detected_devices: List[USBDeviceInfo]
    recommended_device: Optional[USBDeviceInfo] = None
    auto_connected: bool = False
    connection_info: Optional[Dict[str, Any]] = None

class USBMonitor:
    """Universal USB Monitor class - works with ANY USB device"""
    
    def __init__(self):
        self.serial_connection = None
        self.is_connected = False
        self.device_info = {}
        self.latest_data = None
        self.data_format = "auto"
        self.connection_history = []
        self.supported_baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        
        # Common device patterns for auto-detection
        self.device_patterns = {
            "arduino": {"manufacturer": ["Arduino", "Adafruit"], "baudrate": 115200},
            "esp32": {"manufacturer": ["Espressif", "LilyGO"], "baudrate": 115200},
            "raspberry_pi": {"manufacturer": ["Raspberry Pi"], "baudrate": 115200},
            "sensor": {"description": ["sensor", "temp", "humidity", "pressure"], "baudrate": 9600},
            "gps": {"description": ["gps", "navigation"], "baudrate": 9600},
            "generic": {"baudrate": 115200}
        }
        
    def get_available_devices(self) -> List[USBDeviceInfo]:
        """Get list of all available USB devices with enhanced detection"""
        # Check for cloud environment first
        if os.getenv('RENDER') or os.getenv('CLOUD') or not SERIAL_AVAILABLE:
            logger.info("Cloud environment detected or pyserial not available. Using cloud devices.")
            return self._get_cloud_devices()
        
        try:
            ports = serial.tools.list_ports.comports()
            devices = []
            
            for port in ports:
                device_type, recommended_baudrate, supported_formats = self._detect_device_type(port)
                
                device_info = USBDeviceInfo(
                    device=port.device,
                    description=port.description or "Unknown Device",
                    manufacturer=port.manufacturer,
                    vid=port.vid,
                    pid=port.pid,
                    serial_number=port.serial_number,
                    location=port.location,
                    hwid=port.hwid,
                    is_connected=(port.device == self.device_info.get('device', '')),
                    device_type=device_type,
                    recommended_baudrate=recommended_baudrate,
                    supported_formats=supported_formats
                )
                devices.append(device_info)
            
            # If no real devices found in cloud-like environment, use cloud devices
            if not devices and (os.getenv('RENDER') or os.getenv('CLOUD')):
                logger.info("No real USB devices found in cloud environment. Using cloud devices.")
                return self._get_cloud_devices()
            
            return devices
        except Exception as e:
            logger.error(f"Failed to detect USB devices: {e}")
            return self._get_cloud_devices()
    
    def _get_cloud_devices(self) -> List[USBDeviceInfo]:
        """Get cloud devices for environments without real USB access"""
        cloud_devices = [
            USBDeviceInfo(
                device="/dev/cloud/cp2102",
                description="CP2102 USB to UART Bridge Controller",
                manufacturer="Silicon Labs",
                vid=0x10C4,
                pid=0xEA60,
                serial_number="CLOUD001",
                location="cloud-1",
                hwid="CLOUD VID:PID=10C4:EA60",
                is_connected=False,
                device_type="generic",
                recommended_baudrate=115200,
                supported_formats=["json", "text", "csv", "binary"]
            ),
            USBDeviceInfo(
                device="/dev/cloud/sensor",
                description="Temperature Sensor",
                manufacturer="Cloud Labs",
                vid=0x1234,
                pid=0x5678,
                serial_number="CLOUD002",
                location="cloud-2",
                hwid="CLOUD VID:PID=1234:5678",
                is_connected=False,
                device_type="sensor",
                recommended_baudrate=9600,
                supported_formats=["json", "text"]
            )
        ]
        return cloud_devices
    
    def _connect_cloud_device(self, device_path: str, baudrate: int = None) -> bool:
        """Connect to cloud device simulation"""
        logger.info(f"🔌 Connecting to cloud device: {device_path}")
        
        # Simulate connection delay
        time.sleep(0.5)
        
        # Set cloud connection
        self.is_connected = True
        self.device_info = {
            "device": device_path,
            "description": "Cloud Device Simulation",
            "baudrate": baudrate or 115200,
            "timestamp": datetime.now().isoformat(),
            "environment": "cloud"
        }
        
        logger.info(f"✅ Successfully connected to cloud device: {device_path}")
        return True
    
    def _get_cloud_data(self, data_format: str = "auto") -> USBDataResponse:
        """Generate cloud sensor data"""
        import random
        
        cloud_data = {
            "timestamp": datetime.now().isoformat(),
            "temperature": round(random.uniform(20.0, 35.0), 2),
            "humidity": round(random.uniform(40.0, 80.0), 2),
            "pressure": round(random.uniform(980.0, 1020.0), 2),
            "battery_voltage": round(random.uniform(3.2, 4.2), 2),
            "signal_strength": random.randint(-80, -30),
            "device_id": "CLOUD_DEVICE_001",
            "status": "active"
        }
        
        return USBDataResponse(
            timestamp=cloud_data["timestamp"],
            data_size=len(json.dumps(cloud_data)),
            raw_data=json.dumps(cloud_data),
            formatted_data=cloud_data,
            data_type="json",
            device_info=self.device_info,
            sensor_data=cloud_data,
            temp=cloud_data["temperature"],
            battery_v=cloud_data["battery_voltage"]
        )
    
    def _detect_device_type(self, port) -> tuple:
        """Detect device type and recommended settings"""
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        
        # Check against known patterns
        for device_type, pattern in self.device_patterns.items():
            if device_type == "generic":
                continue
                
            # Check manufacturer match
            if "manufacturer" in pattern:
                for manu in pattern["manufacturer"]:
                    if manu.lower() in manufacturer:
                        return device_type, pattern["baudrate"], ["json", "text", "csv"]
            
            # Check description match
            if "description" in pattern:
                for desc in pattern["description"]:
                    if desc in description:
                        return device_type, pattern["baudrate"], ["json", "text", "csv"]
        
        # Default to generic
        return "generic", 115200, ["json", "text", "csv", "binary"]
    
    def auto_detect_and_connect(self) -> DeviceDetectionResponse:
        """Automatically detect and connect to the best available device"""
        devices = self.get_available_devices()
        
        if not devices:
            return DeviceDetectionResponse(
                detected_devices=[],
                recommended_device=None,
                auto_connected=False,
                connection_info={"error": "No USB devices found"}
            )
        
        # Find the best device to connect to
        recommended_device = None
        auto_connected = False
        connection_info = {}
        
        # Priority order: Arduino/ESP32 > Sensors > Generic
        priority_devices = ["arduino", "esp32", "raspberry_pi", "sensor", "gps", "generic"]
        
        for device_type in priority_devices:
            for device in devices:
                if device.device_type == device_type:
                    recommended_device = device
                    break
            if recommended_device:
                break
        
        if not recommended_device:
            recommended_device = devices[0]  # Fallback to first device
        
        # Try to auto-connect to recommended device
        if recommended_device:
            success = self.connect_to_device(
                recommended_device.device, 
                recommended_device.recommended_baudrate
            )
            auto_connected = success
            connection_info = {
                "attempted_device": recommended_device.device,
                "baudrate": recommended_device.recommended_baudrate,
                "success": success
            }
        
        return DeviceDetectionResponse(
            detected_devices=devices,
            recommended_device=recommended_device,
            auto_connected=auto_connected,
            connection_info=connection_info
        )
    
    def connect_to_device(self, device_path: str, baudrate: int = None, auto_detect_baudrate: bool = True) -> bool:
        """Universal device connection - works with any USB device"""
        try:
            # Disconnect existing connection if any
            if self.is_connected:
                self.disconnect()
            
            # Check for cloud environment or pyserial availability
            if os.getenv('RENDER') or os.getenv('CLOUD') or not SERIAL_AVAILABLE:
                logger.info("Cloud environment detected or pyserial not available. Using cloud device simulation.")
                return self._connect_cloud_device(device_path, baudrate)
            
            # Handle different OS device paths
            device_path = self._normalize_device_path(device_path)
            
            # Auto-detect baudrate if not provided
            if baudrate is None or auto_detect_baudrate:
                baudrate = self._detect_baudrate(device_path)
            
            logger.info(f"🔌 Connecting to {device_path} at {baudrate} baud...")
            
            # Try multiple connection strategies
            connection_strategies = [
                {"timeout": 1, "parity": serial.PARITY_NONE, "stopbits": serial.STOPBITS_ONE, "bytesize": serial.EIGHTBITS},
                {"timeout": 2, "parity": serial.PARITY_EVEN, "stopbits": serial.STOPBITS_ONE, "bytesize": serial.EIGHTBITS},
                {"timeout": 1, "parity": serial.PARITY_NONE, "stopbits": serial.STOPBITS_TWO, "bytesize": serial.SEVENBITS},
            ]
            
            for strategy in connection_strategies:
                try:
                    self.serial_connection = serial.Serial(
                        port=device_path,
                        baudrate=baudrate,
                        **strategy
                    )
                    
                    # Wait for connection to stabilize
                    time.sleep(1)
                    
                    if self.serial_connection.is_open:
                        self.is_connected = True
                        
                        # Get enhanced device info
                        self.device_info = self._get_enhanced_device_info(device_path, baudrate, strategy)
                        
                        # Record connection in history
                        self.connection_history.append({
                            "device": device_path,
                            "baudrate": baudrate,
                            "timestamp": datetime.now().isoformat(),
                            "success": True
                        })
                        
                        logger.info(f"✅ Successfully connected to {device_path} using strategy: {strategy}")
                        return True
                        
                except Exception as e:
                    logger.debug(f"Connection strategy failed: {strategy}, error: {e}")
                    if self.serial_connection:
                        try:
                            self.serial_connection.close()
                        except:
                            pass
                    continue
            
            # All strategies failed
            self.connection_history.append({
                "device": device_path,
                "baudrate": baudrate,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": "All connection strategies failed"
            })
            
            logger.error("❌ All connection strategies failed")
            return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def _normalize_device_path(self, device_path: str) -> str:
        """Normalize device path for different operating systems"""
        system = platform.system().lower()
        
        if system == "windows":
            # Windows COM ports
            if not device_path.startswith("COM"):
                if device_path.startswith("/dev/"):
                    # Convert /dev/ttyUSB0 to COM format (approximation)
                    device_path = device_path.replace("/dev/ttyUSB", "COM").replace("/dev/ttyACM", "COM")
                else:
                    device_path = f"COM{device_path}"
        elif system in ["linux", "darwin"]:  # Linux/macOS
            # Unix-style paths
            if not device_path.startswith("/dev/"):
                device_path = f"/dev/{device_path}"
        
        return device_path
    
    def _detect_baudrate(self, device_path: str) -> int:
        """Auto-detect optimal baudrate for device"""
        # Try common baudrates in order of likelihood
        test_baudrates = [115200, 9600, 57600, 38400, 19200, 230400, 460800, 921600]
        
        for baudrate in test_baudrates:
            try:
                test_connection = serial.Serial(
                    port=device_path,
                    baudrate=baudrate,
                    timeout=0.5
                )
                test_connection.close()
                logger.info(f"🔍 Detected baudrate: {baudrate}")
                return baudrate
            except:
                continue
        
        # Default fallback
        return 115200
    
    def _get_enhanced_device_info(self, device_path: str, baudrate: int, connection_params: dict) -> dict:
        """Get enhanced device information"""
        ports = serial.tools.list_ports.comports()
        device_info = {
            'device': device_path,
            'baudrate': baudrate,
            'connection_params': connection_params,
            'connection_time': datetime.now().isoformat(),
            'os': platform.system(),
            'platform': platform.platform()
        }
        
        # Find matching port info
        for port in ports:
            if port.device == device_path:
                device_info.update({
                    'description': port.description,
                    'manufacturer': port.manufacturer,
                    'vid': port.vid,
                    'pid': port.pid,
                    'serial_number': port.serial_number,
                    'location': port.location,
                    'hwid': port.hwid
                })
                break
        
        return device_info
    
    def disconnect(self):
        """Disconnect from USB device"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            self.device_info = {}
            logger.info("🔌 Disconnected from USB device")
    
    def read_data(self, data_format: str = "auto") -> Optional[USBDataResponse]:
        """Universal data reading - works with any data format"""
        if not self.is_connected:
            return None
        
        # Check for cloud environment or pyserial availability
        if os.getenv('RENDER') or os.getenv('CLOUD') or not SERIAL_AVAILABLE:
            logger.info("Cloud environment detected or pyserial not available. Using cloud data simulation.")
            return self._get_cloud_data(data_format)
        
        if not self.serial_connection:
            return None
        
        try:
            raw_data = None
            data_bytes = None
            
            # Multiple reading strategies
            if self.serial_connection.in_waiting > 0:
                # Read available bytes
                data_bytes = self.serial_connection.read(self.serial_connection.in_waiting)
                raw_data = data_bytes.decode('utf-8', errors='ignore').strip()
            else:
                # Try reading a line
                try:
                    line = self.serial_connection.readline()
                    if line:
                        data_bytes = line
                        raw_data = line.decode('utf-8', errors='ignore').strip()
                except:
                    pass
            
            if not raw_data:
                return None
            
            # Print raw data to terminal for debugging
            print(f"📊 RAW DATA: {raw_data}")
            
            # Parse data based on format
            parsed_data = self.parse_universal_data(raw_data, len(data_bytes), data_format)
            if parsed_data:
                self.latest_data = parsed_data
                return parsed_data
            
            return None
                
        except Exception as e:
            logger.error(f"Read error: {e}")
            return None
    
    def parse_universal_data(self, raw_data: str, data_size: int, data_format: str = "auto") -> Optional[USBDataResponse]:
        """Universal data parsing - handles JSON, CSV, text, binary"""
        try:
            # Clean the data
            clean_data = raw_data.strip().replace('\x00', '')
            
            if not clean_data:
                return None
            
            # Auto-detect format if not specified
            if data_format == "auto":
                data_format = self._detect_data_format(clean_data)
            
            # Parse based on detected/specified format
            parsed_result = None
            sensor_data = {}
            
            if data_format == "json":
                parsed_result = self._parse_json_data(clean_data)
            elif data_format == "csv":
                parsed_result = self._parse_csv_data(clean_data)
            elif data_format == "key_value":
                parsed_result = self._parse_key_value_data(clean_data)
            elif data_format == "binary":
                parsed_result = self._parse_binary_data(clean_data)
            elif data_format == "text":
                parsed_result = self._parse_text_data(clean_data)
            
            # Extract sensor data from parsed result
            if parsed_result:
                sensor_data = self._extract_sensor_data(parsed_result)
            
            # Create response
            response = USBDataResponse(
                timestamp=datetime.now().strftime('%H:%M:%S.%f')[:-3],
                data_size=data_size,
                raw_data=clean_data,
                formatted_data=parsed_result,
                data_type=data_format,
                device_info=self.device_info,
                sensor_data=sensor_data
            )
            
            # Backward compatibility - extract common fields
            if sensor_data:
                response.soc = sensor_data.get('soc') or sensor_data.get('state_of_charge') or sensor_data.get('battery_level')
                response.battery_i = sensor_data.get('battery_i') or sensor_data.get('current') or sensor_data.get('amp')
                response.battery_v = sensor_data.get('battery_v') or sensor_data.get('voltage') or sensor_data.get('volt')
                response.temp = sensor_data.get('temp') or sensor_data.get('temperature') or sensor_data.get('celsius')
                response.rpm = sensor_data.get('rpm') or sensor_data.get('speed') or sensor_data.get('revolution')
            
            return response
            
        except Exception as e:
            logger.error(f"Universal data parsing error: {e}")
            return None
    
    def _detect_data_format(self, data: str) -> str:
        """Auto-detect data format"""
        data_lower = data.lower().strip()
        
        # JSON detection
        if (data.startswith('{') and data.endswith('}')) or (data.startswith('[') and data.endswith(']')):
            try:
                json.loads(data)
                return "json"
            except:
                pass
        
        # CSV detection
        if ',' in data and len(data.split(',')) >= 2:
            try:
                csv.reader(io.StringIO(data))
                return "csv"
            except:
                pass
        
        # Key-Value detection
        if '=' in data or ':' in data:
            return "key_value"
        
        # Binary detection (contains non-printable characters)
        if any(ord(c) < 32 or ord(c) > 126 for c in data if c not in ['\n', '\r', '\t']):
            return "binary"
        
        # Default to text
        return "text"
    
    def _parse_json_data(self, data: str) -> Optional[Dict]:
        """Parse JSON data"""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            # Try to extract JSON from mixed data
            json_match = re.search(r'\{[^}]*\}', data)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        return None
    
    def _parse_csv_data(self, data: str) -> Optional[Dict]:
        """Parse CSV data"""
        try:
            reader = csv.reader(io.StringIO(data))
            rows = list(reader)
            if len(rows) >= 2:
                # Assume first row is headers
                headers = rows[0]
                values = rows[1] if len(rows) > 1 else []
                return dict(zip(headers, values))
        except:
            pass
        return None
    
    def _parse_key_value_data(self, data: str) -> Optional[Dict]:
        """Parse key=value or key:value data"""
        result = {}
        try:
            # Split by common separators
            pairs = re.split(r'[,;\n\r\t]+', data)
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    result[key.strip()] = value.strip()
                elif ':' in pair:
                    key, value = pair.split(':', 1)
                    result[key.strip()] = value.strip()
        except:
            pass
        return result if result else None
    
    def _parse_binary_data(self, data: str) -> Optional[Dict]:
        """Parse binary data (hex representation)"""
        try:
            # Convert to hex and group by bytes
            hex_data = data.encode().hex()
            return {"hex": hex_data, "binary_length": len(data)}
        except:
            return None
    
    def _parse_text_data(self, data: str) -> Optional[Dict]:
        """Parse plain text data"""
        return {"text": data, "length": len(data)}
    
    def _extract_sensor_data(self, parsed_data: Dict) -> Dict[str, Union[str, int, float]]:
        """Extract common sensor data fields"""
        sensor_data = {}
        
        if not parsed_data:
            return sensor_data
        
        # Common sensor field mappings
        field_mappings = {
            'temperature': ['temp', 'temperature', 'celsius', 'fahrenheit', 'c', 'f'],
            'humidity': ['humidity', 'hum', 'rh', 'relative_humidity'],
            'pressure': ['pressure', 'barometric', 'atm', 'pa', 'hpa'],
            'voltage': ['voltage', 'volt', 'v', 'battery_v', 'volts'],
            'current': ['current', 'amp', 'ampere', 'ma', 'battery_i'],
            'state_of_charge': ['soc', 'battery_level', 'charge', 'capacity'],
            'speed': ['rpm', 'speed', 'velocity', 'revolution'],
            'distance': ['distance', 'dist', 'range', 'meters', 'feet'],
            'light': ['light', 'lux', 'brightness', 'illumination'],
            'sound': ['sound', 'db', 'decibel', 'noise', 'audio']
        }
        
        # Extract values using mappings
        for sensor_type, field_names in field_mappings.items():
            for field_name in field_names:
                if field_name in parsed_data:
                    try:
                        value = parsed_data[field_name]
                        # Try to convert to number
                        if isinstance(value, str):
                            # Remove units and convert
                            numeric_value = re.sub(r'[^\d.-]', '', str(value))
                            if numeric_value:
                                sensor_data[sensor_type] = float(numeric_value)
                            else:
                                sensor_data[sensor_type] = value
                        else:
                            sensor_data[sensor_type] = value
                        break
                    except:
                        sensor_data[sensor_type] = parsed_data[field_name]
        
        return sensor_data
    

# Global USB monitor instance
usb_monitor = USBMonitor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 USB API Server starting...")
    yield
    logger.info("🛑 USB API Server shutting down...")
    if usb_monitor:
        usb_monitor.disconnect()

# Create FastAPI app
app = FastAPI(
    title="Universal USB Device API",
    description="Universal API that works with ANY USB device - automatically detects and connects. Supports JSON, CSV, text, and binary data formats.",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files removed - no web interface

# ===============================
# 4 ESSENTIAL API ENDPOINTS
# ===============================

@app.get("/")
async def root():
    """Root endpoint - Universal USB Device API"""
    return {
        "message": "Universal USB Device API",
        "version": "2.0.0",
        "description": "Works with ANY USB device - automatically detects and connects",
        "features": [
            "Auto-detects device type and optimal settings",
            "Supports JSON, CSV, text, and binary data formats",
            "Cross-platform (Windows, Linux, macOS)",
            "Universal sensor data extraction",
            "Multiple connection strategies"
        ],
        "endpoints": {
            "health": "/health",
            "devices": "/devices", 
            "auto_detect": "/auto-detect",
            "usb_inserted": "/usb-inserted",
            "monitor_usb": "/monitor-usb",
            "connect": "/connect",
            "data": "/data",
            "disconnect": "/disconnect"
        },
        "usb_insertion_flow": {
            "step_1": "Insert your USB device",
            "step_2": "Call POST /usb-inserted to auto-detect and connect",
            "step_3": "Call GET /data to read data from the device",
            "step_4": "Call POST /disconnect when done"
        },
        "usage": "Insert USB device → POST /usb-inserted → GET /data → POST /disconnect"
    }

@app.get("/health")
async def health_check():
    """1. Health Check Endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "2.0.0",
        "device_connected": usb_monitor.is_connected,
        "connected_device": usb_monitor.device_info.get('device') if usb_monitor.is_connected else None,
        "platform": platform.system(),
        "total_connections": len(usb_monitor.connection_history)
    }

@app.get("/devices", response_model=List[USBDeviceInfo])
async def list_usb_devices():
    """2. List all connected USB devices with enhanced detection"""
    try:
        devices = usb_monitor.get_available_devices()
        logger.info(f"Found {len(devices)} USB devices")
        return devices
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auto-detect", response_model=DeviceDetectionResponse)
async def auto_detect_devices():
    """3. Auto-detect and connect to the best available USB device"""
    try:
        result = usb_monitor.auto_detect_and_connect()
        logger.info(f"Auto-detection result: {len(result.detected_devices)} devices found, connected: {result.auto_connected}")
        return result
    except Exception as e:
        logger.error(f"Auto-detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/usb-inserted")
async def handle_usb_inserted():
    """Handle USB device insertion - auto-detect and connect to newly inserted device"""
    try:
        # Get current devices
        devices = usb_monitor.get_available_devices()
        
        if not devices:
            return {
                "status": "no_devices",
                "message": "No USB devices detected. Please insert a USB device and try again.",
                "devices_found": 0
            }
        
        # Find the best device to connect to
        best_device = None
        for device in devices:
            if not device.is_connected:  # Find unconnected device
                best_device = device
                break
        
        if not best_device:
            return {
                "status": "all_connected",
                "message": "All detected USB devices are already connected.",
                "devices_found": len(devices)
            }
        
        # Auto-connect to the best available device
        success = usb_monitor.connect_to_device(
            best_device.device,
            best_device.recommended_baudrate
        )
        
        if success:
            return {
                "status": "connected",
                "message": f"Successfully connected to USB device: {best_device.description}",
                "device": {
                    "path": best_device.device,
                    "description": best_device.description,
                    "manufacturer": best_device.manufacturer,
                    "vid": best_device.vid,
                    "pid": best_device.pid,
                    "baudrate": best_device.recommended_baudrate
                },
                "next_steps": {
                    "get_data": "/data",
                    "health_check": "/health",
                    "disconnect": "/disconnect"
                }
            }
        else:
            return {
                "status": "connection_failed",
                "message": f"Failed to connect to USB device: {best_device.device}",
                "device": best_device.device,
                "suggestion": "Try connecting manually with /connect endpoint"
            }
            
    except Exception as e:
        logger.error(f"USB insertion handling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/connect")
async def choose_usb_device(request: ConnectionRequest):
    """4. Connect to a specific USB device (manual connection)"""
    try:
        # Use auto-detect if no device specified
        if request.auto_detect and not request.device_path:
            result = usb_monitor.auto_detect_and_connect()
            if result.auto_connected:
                return {
                    "message": "Successfully auto-connected to device",
                    "device": usb_monitor.device_info,
                    "status": "connected",
                    "auto_detected": True,
                    "detection_result": result
                }
            else:
                raise HTTPException(status_code=400, detail="Auto-detection failed")
        
        # Manual connection
        if not request.device_path:
            raise HTTPException(status_code=400, detail="Device path is required for manual connection")
        
        success = usb_monitor.connect_to_device(
            request.device_path, 
            request.baudrate,
            auto_detect_baudrate=(request.baudrate is None)
        )
        
        if success:
            return {
                "message": "Successfully connected to device",
                "device": usb_monitor.device_info,
                "status": "connected",
                "auto_detected": False
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to connect to device")
    except Exception as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/disconnect")
async def disconnect_device():
    """5. Disconnect from current USB device"""
    try:
        if not usb_monitor.is_connected:
            return {"message": "No device connected", "status": "disconnected"}
        
        device_info = usb_monitor.device_info.copy()
        usb_monitor.disconnect()
        
        return {
            "message": "Successfully disconnected from device",
            "previous_device": device_info,
            "status": "disconnected"
        }
    except Exception as e:
        logger.error(f"Disconnection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data")
async def get_usb_data(data_format: str = Query("auto", description="Data format: auto, json, csv, text, binary")):
    """6. Get data from connected USB device with universal parsing"""
    if not usb_monitor.is_connected:
        raise HTTPException(status_code=400, detail="No device connected. Use /auto-detect or /connect first.")
    
    try:
        # Try to read new data with specified format
        data = usb_monitor.read_data(data_format)
        if data:
            return data
        elif usb_monitor.latest_data:
            return usb_monitor.latest_data
        else:
            return {
                "message": "No data available", 
                "timestamp": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "device_connected": True,
                "device_info": usb_monitor.device_info,
                "suggestion": "Make sure your device is sending data. Try different data_format values."
            }
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitor-usb")
async def monitor_usb_devices():
    """Monitor USB devices - check for newly inserted devices and auto-connect"""
    try:
        # Get current devices
        devices = usb_monitor.get_available_devices()
        
        # Check if we have any new devices
        new_devices = []
        for device in devices:
            if not device.is_connected:
                new_devices.append(device)
        
        # If we have new devices and no current connection, auto-connect to the first one
        if new_devices and not usb_monitor.is_connected:
            best_device = new_devices[0]
            success = usb_monitor.connect_to_device(
                best_device.device,
                best_device.recommended_baudrate
            )
            
            if success:
                return {
                    "status": "auto_connected",
                    "message": f"Auto-connected to newly detected device: {best_device.description}",
                    "connected_device": {
                        "path": best_device.device,
                        "description": best_device.description,
                        "manufacturer": best_device.manufacturer,
                        "vid": best_device.vid,
                        "pid": best_device.pid
                    },
                    "all_devices": len(devices),
                    "new_devices": len(new_devices),
                    "next_step": "Call /data to read from the connected device"
                }
        
        return {
            "status": "monitoring",
            "message": f"Found {len(devices)} USB devices, {len(new_devices)} available for connection",
            "connected": usb_monitor.is_connected,
            "connected_device": usb_monitor.device_info.get('device') if usb_monitor.is_connected else None,
            "available_devices": [
                {
                    "device": d.device,
                    "description": d.description,
                    "manufacturer": d.manufacturer,
                    "connected": d.is_connected
                } for d in new_devices
            ],
            "suggestion": "Insert a USB device and call this endpoint again, or use /usb-inserted for automatic connection"
        }
        
    except Exception as e:
        logger.error(f"USB monitoring error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "usb_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
