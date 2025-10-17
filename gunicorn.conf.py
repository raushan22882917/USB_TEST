# Gunicorn configuration file for USB API deployment

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "usb_api"

# Server mechanics
daemon = False
pidfile = "/tmp/usb_api.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
