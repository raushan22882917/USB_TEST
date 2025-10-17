# USB API Deployment Guide

This guide explains how to deploy the USB API using Gunicorn for production environments.

## Prerequisites

- Python 3.8+
- pip
- USB devices connected to the system

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python -c "import gunicorn; print('Gunicorn installed successfully')"
   ```

## Deployment Options

### Option 1: Using the deployment script (Recommended)

```bash
python start_server.py
```

This will start the server with optimized settings for production.

### Option 2: Using Gunicorn directly

```bash
gunicorn usb_api:app -c gunicorn.conf.py
```

### Option 3: Using Gunicorn with custom settings

```bash
gunicorn usb_api:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 30 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
```

## Configuration

The `gunicorn.conf.py` file contains production-ready settings:

- **Workers**: 4 worker processes for handling concurrent requests
- **Worker Class**: UvicornWorker for ASGI support
- **Timeout**: 30 seconds for request timeout
- **Memory Management**: Workers restart after 1000 requests
- **Logging**: Logs to stdout/stderr for container-friendly deployment

## Environment Variables

You can customize the deployment using environment variables:

```bash
export BIND_ADDRESS="0.0.0.0:8000"
export WORKERS=4
export LOG_LEVEL="info"
```

## Docker Deployment (Optional)

If you want to containerize the application:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_server.py"]
```

## Monitoring

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`
- **Process Monitoring**: Use `ps aux | grep gunicorn` to monitor processes

## Troubleshooting

1. **Permission Issues**: Ensure the user has access to USB devices
2. **Port Conflicts**: Change the port in configuration if 8000 is in use
3. **Worker Issues**: Increase timeout if workers are being killed

## Performance Tuning

- **Workers**: Adjust based on CPU cores (2 × CPU cores + 1)
- **Memory**: Monitor memory usage and adjust max-requests
- **Timeout**: Increase for slow USB devices

## Security Considerations

- Run behind a reverse proxy (nginx/Apache) for HTTPS
- Use firewall rules to restrict access
- Consider authentication for production use
