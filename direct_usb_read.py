#!/usr/bin/env python3
"""
Direct USB Data Reader - Auto-Detect USB Devices
Reads data directly from USB device with automatic detection
"""

import serial
import serial.tools.list_ports
import json
import time
from datetime import datetime

def detect_usb_device():
    """Auto-detect USB serial devices"""
    ports = serial.tools.list_ports.comports()
    usb_ports = []
    
    for port in ports:
        # Filter for USB serial devices (exclude system ports)
        if (port.device.startswith('/dev/cu.usb') or 
            port.device.startswith('/dev/cu.USB') or
            'USB' in port.description.upper() or
            'CP210' in port.description or
            'FTDI' in port.description or
            'CH340' in port.description):
            usb_ports.append(port)
    
    return usb_ports

def read_usb_data():
    """Read data directly from USB device with automatic detection"""
    try:
        # Auto-detect USB devices
        usb_ports = detect_usb_device()
        
        if not usb_ports:
            print("❌ No USB serial devices found!")
            print("Please connect your USB device and try again.")
            return
        
        # Use the first detected USB device
        selected_port = usb_ports[0]
        device_path = selected_port.device
        
        print("🚀 Direct USB Data Reader Started (Auto-Detect)")
        print(f"📊 Detected USB device: {selected_port.description}")
        print(f"📊 Reading from: {device_path}")
        print("📊 Format: timestamp {soc, battery_i, battery_v, temp, rpm}")
        print("=" * 60)
        
        # Try different baudrates
        baudrates = [115200, 9600, 57600, 38400, 19200]
        ser = None
        
        for baudrate in baudrates:
            try:
                print(f"🔌 Trying to connect at {baudrate} baud...")
                ser = serial.Serial(device_path, baudrate, timeout=2)
                print(f"✅ Connected successfully at {baudrate} baud!")
                break
            except Exception as e:
                print(f"❌ Failed at {baudrate} baud: {e}")
                continue
        
        if not ser:
            print("❌ Could not connect to device at any baudrate!")
            return
        
        buffer = ""
        last_valid_data = None
        
        while True:
            try:
                # Read available data
                if ser.in_waiting > 0:
                    raw_data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    buffer += raw_data
                    
                    # Process complete lines
                    while '\n' in buffer or '\r' in buffer:
                        # Find the first complete line
                        line_end = buffer.find('\n')
                        if line_end == -1:
                            line_end = buffer.find('\r')
                        
                        if line_end != -1:
                            line = buffer[:line_end].strip()
                            buffer = buffer[line_end + 1:]
                            
                            if line:
                                # Generate current timestamp
                                now = datetime.now()
                                timestamp = now.strftime("%H:%M:%S.%f")[:-3]
                                
                                try:
                                    # Try to parse as JSON
                                    data = json.loads(line)
                                    
                                    # Only print if data is different from last valid data
                                    if last_valid_data != data:
                                        # Format and print output
                                        output = f'{timestamp} {{"soc":{data["soc"]},"battery_i":{data["battery_i"]},"battery_v":{data["battery_v"]},"temp":{data["temp"]},"rpm":{data["rpm"]}}}'
                                        print(output)
                                        last_valid_data = data
                                    
                                except json.JSONDecodeError:
                                    # If not valid JSON, skip corrupted data
                                    if len(line) > 10:  # Only log if it looks like partial data
                                        print(f"{timestamp} SKIP: {line[:50]}...")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                        
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error reading data: {e}")
                time.sleep(1)
                
        # Close the serial connection
        if ser:
            ser.close()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your USB device connection and try again.")

if __name__ == "__main__":
    read_usb_data()
