#!/usr/bin/env python3
"""
Deployment script for USB API server
Run with: python start_server.py
"""

import os
import sys
from gunicorn.app.wsgiapp import WSGIApplication

class USBAPIApplication(WSGIApplication):
    """Custom Gunicorn application for USB API"""
    
    def init(self, parser, opts, args):
        """Initialize the application"""
        # Set the application module
        self.cfg.set('bind', '0.0.0.0:8000')
        self.cfg.set('workers', 4)
        self.cfg.set('worker_class', 'uvicorn.workers.UvicornWorker')
        self.cfg.set('timeout', 30)
        self.cfg.set('keepalive', 2)
        self.cfg.set('max_requests', 1000)
        self.cfg.set('max_requests_jitter', 100)
        self.cfg.set('loglevel', 'info')
        self.cfg.set('accesslog', '-')
        self.cfg.set('errorlog', '-')
        self.cfg.set('proc_name', 'usb_api')
        
        # Set the WSGI application
        self.app_uri = 'usb_api:app'
        
        # Load configuration from file if it exists
        config_file = 'gunicorn.conf.py'
        if os.path.exists(config_file):
            self.cfg.set('config', config_file)

def main():
    """Main entry point"""
    print("🚀 Starting USB API Server with Gunicorn...")
    print("📡 Server will be available at: http://0.0.0.0:8000")
    print("📋 API Documentation: http://0.0.0.0:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        USBAPIApplication().run()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
