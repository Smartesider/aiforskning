# 🚀 Quick Deploy Commands - Ubuntu Server

## Essential Commands for testsider.no Deployment

### 1. Initial Setup (Run Once)
```bash
# Connect to server
ssh username@testsider.no

# Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-venv nginx ufw

# Clone project
cd /var/www/
sudo git clone https://github.com/Smartesider/aiforskning.git
sudo chown -R $USER:$USER /var/www/aiforskning
cd /var/www/aiforskning

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn supervisor

# Test installation
python system_check.py
```

### 2. Configure Services
```bash
# Create Gunicorn config (copy from deployment guide)
# Create Supervisor config (copy from deployment guide) 
# Create Nginx config (copy from deployment guide)

# Enable services
sudo supervisorctl reread && sudo supervisorctl update
sudo ln -s /etc/nginx/sites-available/aiforskning /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### 3. Security & Firewall
```bash
# Setup firewall
sudo ufw allow ssh && sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Set permissions
sudo chown -R www-data:www-data /var/www/aiforskning
sudo chmod -R 755 /var/www/aiforskning
```

### 4. Start & Test
```bash
# Start services
sudo supervisorctl start aiforskning
sudo systemctl start nginx

# Test deployment
curl http://localhost/health
curl http://testsider.no/health
```

### 5. Common Maintenance Commands
```bash
# Update application
cd /var/www/aiforskning
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart aiforskning

# Check logs
sudo tail -f /var/log/aiforskning/error.log
sudo tail -f /var/log/nginx/error.log

# Check service status
sudo supervisorctl status aiforskning
sudo systemctl status nginx

# Restart services
sudo supervisorctl restart aiforskning
sudo systemctl restart nginx
```

### 🌐 Access Points After Deployment:
- **Main Dashboard**: http://testsider.no
- **Vue Dashboard**: http://testsider.no/vue
- **Advanced Analytics**: http://testsider.no/advanced
- **Health Check**: http://testsider.no/health

### 🆘 Emergency Commands:
```bash
# If something breaks
sudo supervisorctl stop aiforskning
sudo systemctl stop nginx

# Check what's wrong
python system_check.py
sudo nginx -t

# Restart everything
sudo systemctl start nginx
sudo supervisorctl start aiforskning
```

### 📞 Get Help:
```bash
# Run full system validation
python system_check.py

# Test core components
python test_core.py

# View detailed logs
sudo journalctl -u nginx -f
sudo tail -f /var/log/aiforskning/supervisor.log
```

That's it! Follow the full UBUNTU_DEPLOYMENT_GUIDE.md for detailed explanations.
