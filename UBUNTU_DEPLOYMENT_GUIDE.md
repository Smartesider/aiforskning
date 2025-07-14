# 🚀 Complete Ubuntu Server Deployment Guide

## Deploy AI Ethics Testing Framework to testsider.no

This guide will walk you through deploying the AI Ethics Testing Framework to your Ubuntu server step by step.

---

## 📋 Prerequisites

Before starting, make sure you have:
- SSH access to your Ubuntu server (testsider.no)
- Domain pointing to your server
- Basic terminal knowledge

---

## 🔧 Step 1: Connect to Your Server

```bash
# Connect to your Ubuntu server via SSH
ssh username@testsider.no

# Or if you have a specific SSH key:
ssh -i /path/to/your/key username@testsider.no
```

---

## 📦 Step 2: Update System & Install Dependencies

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git python3 python3-pip python3-venv nginx ufw curl wget

# Install Node.js (for some frontend dependencies)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3 --version
pip3 --version
git --version
nginx -v
```

---

## 🏗️ Step 3: Clone Your Repository

```bash
# Navigate to web directory
cd /var/www/

# Clone your repository
sudo git clone https://github.com/Smartesider/aiforskning.git

# Change ownership to your user
sudo chown -R $USER:$USER /var/www/aiforskning

# Navigate to project directory
cd /var/www/aiforskning
```

---

## 🐍 Step 4: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn supervisor
```

---

## 🔒 Step 5: Configure Environment

```bash
# Create environment configuration
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_APP=src.web_app:create_app
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_PATH=/var/www/aiforskning/ethics_data.db
HOST=0.0.0.0
PORT=5000
EOF

# Set proper permissions
chmod 600 .env
```

---

## 🗄️ Step 6: Initialize Database

```bash
# Make sure you're in the project directory and venv is active
cd /var/www/aiforskning
source venv/bin/activate

# Test the framework
python test_core.py

# Run system check
python system_check.py

# Initialize with demo data (optional)
python demo.py
```

---

## 🌐 Step 7: Configure Gunicorn

Create Gunicorn configuration:

```bash
# Create Gunicorn config
cat > gunicorn.conf.py << 'EOF'
# Gunicorn configuration for AI Ethics Testing Framework

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Application
pythonpath = "/var/www/aiforskning"
wsgi_module = "run_app:app"

# Logging
accesslog = "/var/log/aiforskning/access.log"
errorlog = "/var/log/aiforskning/error.log"
loglevel = "info"

# Process naming
proc_name = "aiforskning"

# Server mechanics
daemon = False
pidfile = "/var/run/aiforskning.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
EOF

# Create log directory
sudo mkdir -p /var/log/aiforskning
sudo chown www-data:www-data /var/log/aiforskning
```

---

## 🔧 Step 8: Configure Supervisor

Create Supervisor configuration for process management:

```bash
# Create supervisor config
sudo cat > /etc/supervisor/conf.d/aiforskning.conf << 'EOF'
[program:aiforskning]
directory=/var/www/aiforskning
command=/var/www/aiforskning/venv/bin/gunicorn --config gunicorn.conf.py run_app:app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/aiforskning/supervisor.log
environment=PATH="/var/www/aiforskning/venv/bin"
EOF

# Update supervisor and start service
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start aiforskning
```

---

## 🌍 Step 9: Configure Nginx

Create Nginx configuration:

```bash
# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Create new site configuration
sudo cat > /etc/nginx/sites-available/aiforskning << 'EOF'
server {
    listen 80;
    server_name testsider.no www.testsider.no;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web:10m rate=1r/s;

    # Root directory
    root /var/www/aiforskning;

    # Static files
    location /static {
        alias /var/www/aiforskning/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API endpoints (rate limited)
    location /api {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }

    # Main application
    location / {
        limit_req zone=web burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }

    # Security - block sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /(src|__pycache__|\.git) {
        deny all;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/aiforskning /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 🔒 Step 10: Configure Firewall

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Check status
sudo ufw status
```

---

## 🔐 Step 11: Set Up SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d testsider.no -d www.testsider.no

# Set up automatic renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🔧 Step 12: Set Proper Permissions

```bash
# Set ownership and permissions
sudo chown -R www-data:www-data /var/www/aiforskning
sudo chmod -R 755 /var/www/aiforskning
sudo chmod 644 /var/www/aiforskning/ethics_data.db

# Secure sensitive files
sudo chmod 600 /var/www/aiforskning/.env
sudo chmod 600 /var/www/aiforskning/gunicorn.conf.py
```

---

## ✅ Step 13: Start All Services

```bash
# Start and enable services
sudo systemctl enable nginx
sudo systemctl enable supervisor
sudo systemctl start nginx
sudo systemctl start supervisor

# Check service status
sudo systemctl status nginx
sudo systemctl status supervisor
sudo supervisorctl status aiforskning
```

---

## 🧪 Step 14: Test Your Deployment

```bash
# Test from server
curl http://localhost/health
curl http://localhost/

# Test from your local machine
curl http://testsider.no/health
curl http://testsider.no/api/models
```

Open your browser and visit:
- `http://testsider.no` - Main dashboard
- `http://testsider.no/vue` - Vue.js dashboard  
- `http://testsider.no/advanced` - Advanced analytics dashboard

---

## 📊 Step 15: Monitor and Maintain

### Check Application Logs:
```bash
# Supervisor logs
sudo tail -f /var/log/aiforskning/supervisor.log

# Application logs
sudo tail -f /var/log/aiforskning/access.log
sudo tail -f /var/log/aiforskning/error.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Application:
```bash
# Restart the application
sudo supervisorctl restart aiforskning

# Restart nginx
sudo systemctl restart nginx
```

### Update Application:
```bash
cd /var/www/aiforskning
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart aiforskning
```

---

## 🚨 Troubleshooting

### If site doesn't load:
1. Check if services are running:
   ```bash
   sudo systemctl status nginx
   sudo supervisorctl status aiforskning
   ```

2. Check logs for errors:
   ```bash
   sudo tail -f /var/log/aiforskning/error.log
   sudo tail -f /var/log/nginx/error.log
   ```

3. Test application directly:
   ```bash
   cd /var/www/aiforskning
   source venv/bin/activate
   python run_app.py
   ```

### If database errors occur:
```bash
cd /var/www/aiforskning
source venv/bin/activate
python system_check.py
```

### Port issues:
```bash
# Check what's using port 5000
sudo netstat -tlnp | grep :5000

# Check if gunicorn is running
ps aux | grep gunicorn
```

---

## 🎉 Congratulations!

Your AI Ethics Testing Framework is now deployed and running on testsider.no!

### Access your application:
- **Main Dashboard**: http://testsider.no
- **Vue Dashboard**: http://testsider.no/vue  
- **Advanced Analytics**: http://testsider.no/advanced
- **API Health Check**: http://testsider.no/health

### Key Features Available:
✅ Neural network visualization  
✅ Moral compass dashboard  
✅ Ethical weather mapping  
✅ Statistical correlation analysis  
✅ Anomaly detection  
✅ Multi-language testing framework  
✅ Adversarial ethics probing  
✅ Cultural bias analysis  
✅ Response quality metrics  
✅ Uncertainty quantification  

The system is production-ready with proper security, monitoring, and scalability configurations.

---

## 📞 Need Help?

If you encounter any issues during deployment, you can:
1. Check the troubleshooting section above
2. Review the application logs
3. Run the system validation: `python system_check.py`
4. Test core functionality: `python test_core.py`

Happy ethical AI testing! 🧠✨
