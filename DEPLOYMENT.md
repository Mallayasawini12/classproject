# EmotiSense Deployment Guide 🚀

This guide covers different deployment options for the EmotiSense application.

## 📋 Table of Contents

1. [Production Server Deployment (Local/VPS)](#production-server-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Windows Service Deployment](#windows-service-deployment)
4. [Systemd Service (Linux)](#systemd-service)
5. [Environment Configuration](#environment-configuration)
6. [Security Considerations](#security-considerations)

---

## 🖥️ Production Server Deployment

### Prerequisites

- Python 3.12+
- Webcam access
- sudo/admin privileges (for system-wide installation)

### Step 1: Prepare the Server

```bash
# Update system packages (Linux)
sudo apt update && sudo apt upgrade -y

# Install system dependencies for OpenCV
sudo apt install -y python3-pip python3-venv libgl1-mesa-glx libglib2.0-0
```

### Step 2: Setup Application

```bash
# Clone/upload your application
cd /opt  # or your preferred location
# Copy your project files here

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install production dependencies
pip install -r requirements-prod.txt
```

### Step 3: Create Logs Directory

```bash
mkdir -p logs
chmod 755 logs
```

### Step 4: Run with Gunicorn

```bash
# Test run
gunicorn --config gunicorn_config.py wsgi:app

# Or run directly
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 wsgi:app
```

### Step 5: Configure Firewall

```bash
# Allow port 5000 (adjust as needed)
sudo ufw allow 5000/tcp
sudo ufw reload
```

---

## 🐳 Docker Deployment

Docker provides a containerized environment for easy deployment.

### Prerequisites

- Docker installed
- Docker Compose installed (optional but recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

### Option 2: Docker CLI

```bash
# Build the image
docker build -t emotisense:latest .

# Run the container (Linux)
docker run -d \
  --name emotisense \
  -p 5000:5000 \
  --device /dev/video0:/dev/video0 \
  --privileged \
  -v $(pwd)/logs:/app/logs \
  emotisense:latest

# Run the container (Windows)
docker run -d ^
  --name emotisense ^
  -p 5000:5000 ^
  --device /dev/video0:/dev/video0 ^
  --privileged ^
  -v %cd%/logs:/app/logs ^
  emotisense:latest

# View logs
docker logs -f emotisense

# Stop container
docker stop emotisense

# Remove container
docker rm emotisense
```

### Docker Management Commands

```bash
# View running containers
docker ps

# Access container shell
docker exec -it emotisense bash

# Restart container
docker restart emotisense

# Update and redeploy
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🪟 Windows Service Deployment

For Windows servers, you can run EmotiSense as a background service.

### Using NSSM (Non-Sucking Service Manager)

1. **Download NSSM**: https://nssm.cc/download
2. **Extract and open Command Prompt as Administrator**

```cmd
# Navigate to NSSM directory
cd C:\path\to\nssm\win64

# Install service
nssm install EmotiSense

# In the NSSM GUI:
# - Path: C:\Users\lenovo\OneDrive\Desktop\FF\.venv\Scripts\gunicorn.exe
# - Startup directory: C:\Users\lenovo\OneDrive\Desktop\FF
# - Arguments: --config gunicorn_config.py wsgi:app

# Start service
nssm start EmotiSense

# Stop service
nssm stop EmotiSense

# Remove service
nssm remove EmotiSense confirm
```

### Using Python Script as Service (Alternative)

Create a batch file `start_emotisense.bat`:

```batch
@echo off
cd /d C:\Users\lenovo\OneDrive\Desktop\FF
call .venv\Scripts\activate.bat
python -c "import os; os.environ['FLASK_HOST']='0.0.0.0'; os.environ['FLASK_PORT']='5000'; os.environ['FLASK_DEBUG']='false'" & python app.py
```

Then schedule it with Task Scheduler to run at startup.

---

## 🐧 Systemd Service (Linux)

For Linux servers running systemd.

### Create Service File

```bash
sudo nano /etc/systemd/system/emotisense.service
```

Add the following content:

```ini
[Unit]
Description=EmotiSense - Real-Time Emotion Detection
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/FF
Environment="PATH=/opt/FF/.venv/bin"
Environment="FLASK_HOST=0.0.0.0"
Environment="FLASK_PORT=5000"
Environment="FLASK_DEBUG=false"
ExecStart=/opt/FF/.venv/bin/gunicorn --config gunicorn_config.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable emotisense

# Start service
sudo systemctl start emotisense

# Check status
sudo systemctl status emotisense

# View logs
sudo journalctl -u emotisense -f

# Stop service
sudo systemctl stop emotisense

# Restart service
sudo systemctl restart emotisense
```

---

## ⚙️ Environment Configuration

You can configure the application using environment variables:

### Available Environment Variables

```bash
# Flask Configuration
FLASK_HOST=0.0.0.0              # Host to bind to (0.0.0.0 for all interfaces)
FLASK_PORT=5000                 # Port to listen on
FLASK_DEBUG=false               # Enable/disable debug mode (false for production)
FLASK_ENV=production            # Environment name

# Path Configuration (if needed)
PYTHONUNBUFFERED=1              # Force Python to output directly (useful for Docker)
```

### Setting Environment Variables

**Linux/Mac:**
```bash
export FLASK_HOST=0.0.0.0
export FLASK_PORT=8080
export FLASK_DEBUG=false
```

**Windows (PowerShell):**
```powershell
$env:FLASK_HOST="0.0.0.0"
$env:FLASK_PORT="8080"
$env:FLASK_DEBUG="false"
```

**Windows (CMD):**
```cmd
set FLASK_HOST=0.0.0.0
set FLASK_PORT=8080
set FLASK_DEBUG=false
```

**Docker (.env file):**
Create a `.env` file in the project root:
```
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

Then update docker-compose.yml to use it:
```yaml
services:
  emotisense:
    env_file:
      - .env
```

---

## 🔒 Security Considerations

### 1. Network Security

```bash
# Use a reverse proxy (Nginx/Apache) for HTTPS
# Example Nginx configuration:
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# Redirect to HTTPS
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Application Security

- **Never run as root** - Use a dedicated user account
- **Keep dependencies updated** - Regularly update packages
- **Environment variables** - Use for sensitive configuration
- **HTTPS only** - Always use SSL/TLS in production
- **Rate limiting** - Implement API rate limiting for public access
- **Authentication** - Add user authentication if needed

### 4. Camera Access Security

- Ensure only authorized users can access the application
- Consider implementing access controls
- Monitor who is accessing the camera feed
- Add audit logging for camera access

---

## 🔧 Troubleshooting

### Camera Not Detected

```bash
# Check camera availability
ls /dev/video*  # Linux
# Should show /dev/video0 or similar

# Test camera with Python
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
# Should print True
```

### Port Already in Use

```bash
# Find process using port 5000
sudo lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Permission Denied (Camera)

```bash
# Add user to video group (Linux)
sudo usermod -a -G video $USER
# Logout and login again
```

### Out of Memory

```bash
# Increase swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📊 Monitoring

### Check Application Status

```bash
# Using systemd
sudo systemctl status emotisense

# Check if app is responding
curl http://localhost:5000/api/emotions

# View application logs
tail -f logs/error.log
tail -f logs/access.log
```

### Performance Monitoring

```bash
# Monitor resource usage
htop  # or top

# Docker resource usage
docker stats emotisense
```

---

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Activate virtual environment
source .venv/bin/activate

# Update dependencies
pip install -r requirements-prod.txt --upgrade

# Restart service
sudo systemctl restart emotisense
# or
docker-compose restart
```

### Backup

```bash
# Backup logs and data
tar -czf emotisense_backup_$(date +%Y%m%d).tar.gz logs/ *.csv *.json

# Backup using rsync
rsync -avz /opt/FF user@backup-server:/backups/emotisense/
```

---

## 🌐 Accessing the Application

After deployment, access EmotiSense at:

- **Local**: http://localhost:5000
- **Network**: http://YOUR_SERVER_IP:5000
- **Domain**: http://yourdomain.com (if configured)

### API Endpoints

- `GET /api/emotions` - Current emotion statistics
- `GET /api/history` - Emotion history
- `POST /api/reset` - Reset statistics
- `GET /api/export/json` - Export data as JSON
- `GET /api/export/csv` - Export data as CSV

---

## 📱 Mobile/Remote Access

For remote access from mobile devices or other networks:

1. **Port Forwarding**: Configure your router to forward port 5000
2. **Dynamic DNS**: Use services like No-IP or DuckDNS for dynamic IP
3. **VPN**: Use Tailscale or WireGuard for secure remote access
4. **Cloudflare Tunnel**: Use Cloudflare for secure public access

---

## ✅ Deployment Checklist

- [ ] Python 3.12+ installed
- [ ] Dependencies installed from requirements-prod.txt
- [ ] Logs directory created
- [ ] Camera access verified
- [ ] Environment variables configured
- [ ] Firewall configured
- [ ] Service/daemon configured
- [ ] HTTPS/SSL configured (if public-facing)
- [ ] Backup system in place
- [ ] Monitoring configured
- [ ] Documentation reviewed

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review application logs in `logs/` directory
- Check system logs (`journalctl` on Linux, Event Viewer on Windows)

---

## 🎉 Quick Start Commands

### Production on Linux
```bash
# Install and run
pip install -r requirements-prod.txt
mkdir -p logs
gunicorn --config gunicorn_config.py wsgi:app
```

### Production with Docker
```bash
# One-line deployment
docker-compose up -d && docker-compose logs -f
```

### Production on Windows
```bash
# Install and run
pip install -r requirements-prod.txt
mkdir logs
gunicorn --config gunicorn_config.py wsgi:app
```

---

**Congratulations! Your EmotiSense application is now deployed! 🎊**
