#!/bin/bash
# AI Ethics Testing Framework - Root-Compatible Quick Installer
# Simplified version that works perfectly as root

set -euo pipefail

# Configuration
DOMAIN_NAME=""
EMAIL=""
INSTALL_DIR="/var/www/aiforskning"
SERVICE_NAME="aiforskning"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --domain) DOMAIN_NAME="$2"; shift 2 ;;
        --email) EMAIL="$2"; shift 2 ;;
        --help) 
            echo "Usage: $0 --domain DOMAIN [--email EMAIL]"
            echo "Example: $0 --domain testsider.no --email admin@testsider.no"
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ -z "$DOMAIN_NAME" ]]; then
    echo "Error: --domain is required"
    echo "Usage: $0 --domain DOMAIN [--email EMAIL]"
    exit 1
fi

if [[ -z "$EMAIL" ]]; then
    EMAIL="admin@$DOMAIN_NAME"
fi

echo "🧠 AI Ethics Testing Framework - Root Installation"
echo "Domain: $DOMAIN_NAME"
echo "Email: $EMAIL"
echo ""

# Install system dependencies
print_status "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx git curl wget ufw supervisor certbot python3-certbot-nginx

# Create application directory
print_status "Setting up application..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone repository
print_status "Downloading latest code..."
if [[ -d ".git" ]]; then
    git pull origin main
else
    git clone https://github.com/Smartesider/aiforskning.git .
fi

# Create virtual environment and install dependencies
print_status "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Set proper permissions
chown -R www-data:www-data "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

# Create systemd service
print_status "Creating systemd service..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=AI Ethics Testing Framework
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 src.web_app:create_app()
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
print_status "Configuring nginx..."
cat > "/etc/nginx/sites-available/$DOMAIN_NAME" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
ln -sf "/etc/nginx/sites-available/$DOMAIN_NAME" "/etc/nginx/sites-enabled/"
rm -f "/etc/nginx/sites-enabled/default"

# Test nginx configuration
if nginx -t; then
    print_status "Nginx configuration is valid"
else
    print_error "Nginx configuration error"
    exit 1
fi

# Configure firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

# Start services
print_status "Starting services..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"
systemctl reload nginx

# Setup SSL with Let's Encrypt
print_status "Setting up SSL certificate..."
if certbot --nginx -d "$DOMAIN_NAME" --email "$EMAIL" --agree-tos --non-interactive --redirect; then
    print_status "SSL certificate installed successfully"
else
    print_warning "SSL setup failed, but application is running on HTTP"
fi

# Final status check
print_status "Checking service status..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "✅ Application is running successfully!"
    echo ""
    echo "🎉 Installation completed!"
    echo ""
    echo "Access your application at:"
    echo "  🌐 https://$DOMAIN_NAME (or http://$DOMAIN_NAME if SSL failed)"
    echo ""
    echo "Management commands:"
    echo "  systemctl status $SERVICE_NAME    # Check status"
    echo "  systemctl restart $SERVICE_NAME   # Restart application"
    echo "  journalctl -u $SERVICE_NAME -f    # View logs"
    echo ""
else
    print_error "Service failed to start"
    systemctl status "$SERVICE_NAME"
    exit 1
fi
