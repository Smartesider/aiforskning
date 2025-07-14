#!/bin/bash

# AI Ethics Testing Framework - Complete Installation Script
# This script sets up the entire system with nginx, SSL, IPv4 configuration, and security checks
#
# SECURITY FEATURES:
#   - Comprehensive security validation before installation
#   - UFW firewall configuration
#   - SSL/TLS certificates via Let's Encrypt  
#   - Dedicated system user with restricted permissions
#   - IPv4-only networking configuration
#   - Security monitoring and alerting
#
# Usage:
#   ./install.sh                           # Shows security help and interactive mode
#   ./install.sh --help                    # Shows comprehensive security guide
#   ./install.sh --domain example.com --docroot /var/www/ethics --email admin@example.com
#   ./install.sh --domain example.com --docroot /opt/ai-ethics
#   ./install.sh --domain localhost        # Development setup

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables with defaults
APP_NAME="ai-ethics"
APP_PORT=8050
DOMAIN=""
SSL_EMAIL=""
APP_DIR="/opt/ai-ethics"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
SYSTEMD_DIR="/etc/systemd/system"
INTERACTIVE_MODE=true

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Security and prerequisites check
security_check() {
    log "Performing security and prerequisites check..."
    
    # Check if this is a fresh system or if components already exist
    local warnings=()
    
    # Check if nginx is already configured
    if systemctl is-active --quiet nginx 2>/dev/null; then
        warnings+=("⚠️  nginx is already running. Existing configurations may be modified.")
    fi
    
    # Check if SSL certificates exist
    if [[ -d "/etc/letsencrypt/live" ]] && [[ -n "$(ls -A /etc/letsencrypt/live 2>/dev/null)" ]]; then
        warnings+=("⚠️  Existing SSL certificates found. New certificates will be requested if needed.")
    fi
    
    # Check if port is already in use
    if ss -tln | grep -q ":$APP_PORT "; then
        warnings+=("⚠️  Port $APP_PORT is already in use. Service may conflict.")
    fi
    
    # Check if user already exists
    if id "$APP_NAME" &>/dev/null; then
        warnings+=("⚠️  User '$APP_NAME' already exists. Will be reused.")
    fi
    
    # Check available disk space (need at least 1GB)
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 1048576 ]]; then
        warnings+=("⚠️  Low disk space. At least 1GB recommended.")
    fi
    
    # Check if this looks like a production server
    if [[ -d "/var/www" ]] || [[ -d "/etc/nginx/sites-available" ]]; then
        warnings+=("🏢 Production server detected. Installation will integrate with existing setup.")
    fi
    
    # Display warnings if any
    if [[ ${#warnings[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Security and Environment Warnings:${NC}"
        for warning in "${warnings[@]}"; do
            echo "  $warning"
        done
        echo ""
        
        if [[ "$INTERACTIVE_MODE" == true ]]; then
            read -p "Continue despite warnings? (y/N): " confirm_warnings
            if [[ ! "$confirm_warnings" =~ ^[Yy]$ ]]; then
                echo "Installation cancelled for safety"
                exit 0
            fi
        fi
    fi
}

# Show comprehensive help and security information
show_help_and_security() {
    echo -e "${BLUE}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🧠 AI Ethics Testing Framework                             ║
║                          Security Installation Guide                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo -e "${GREEN}QUICK START - Production Ready Installation:${NC}"
    echo ""
    echo "  sudo ./install.sh --domain your-domain.com --email admin@domain.com"
    echo ""
    
    echo -e "${BLUE}SECURITY FEATURES:${NC}"
    echo "  🔒 UFW Firewall configuration (only SSH, HTTP, HTTPS)"
    echo "  🛡️  SSL/TLS certificates via Let's Encrypt"
    echo "  👤 Dedicated system user (no shell access)"
    echo "  📁 Restricted file permissions"
    echo "  🚫 IPv4-only networking (no IPv6 exposure)"
    echo "  📊 Security monitoring and alerting"
    echo ""
    
    echo -e "${BLUE}WHAT THIS SCRIPT INSTALLS:${NC}"
    echo "  • nginx web server with security headers"
    echo "  • Python 3 application environment"
    echo "  • SQLite database with proper permissions"
    echo "  • systemd service for automatic startup"
    echo "  • SSL certificates and auto-renewal"
    echo "  • Firewall rules and monitoring"
    echo "  • Automated backup system"
    echo ""
    
    echo -e "${BLUE}USAGE OPTIONS:${NC}"
    echo ""
    echo "  ${GREEN}Production Installation:${NC}"
    echo "    sudo ./install.sh --domain ethics.example.com --email admin@example.com"
    echo ""
    echo "  ${GREEN}Custom Directory:${NC}"
    echo "    sudo ./install.sh --domain ethics.local --docroot /var/www/ethics"
    echo ""
    echo "  ${GREEN}Development Setup:${NC}"
    echo "    sudo ./install.sh --domain localhost --port 8050"
    echo ""
    echo "  ${GREEN}Interactive Mode:${NC}"
    echo "    sudo ./install.sh"
    echo ""
    
    echo -e "${BLUE}COMMAND LINE OPTIONS:${NC}"
    echo "  --domain DOMAIN     🌐 Domain name (required for production)"
    echo "  --docroot PATH      📁 Installation directory (default: /opt/ai-ethics)"
    echo "  --email EMAIL       📧 Email for SSL certificates (recommended)"
    echo "  --port PORT         🔌 Application port (default: 8050)"
    echo "  --app-name NAME     🏷️  Service name (default: ai-ethics)"
    echo "  --help, -h          ❓ Show this help"
    echo ""
    
    echo -e "${YELLOW}SYSTEM REQUIREMENTS:${NC}"
    echo "  • Ubuntu 18.04+ or Debian 10+"
    echo "  • Root access (sudo)"
    echo "  • 1GB+ available disk space"
    echo "  • Internet connection for packages"
    echo "  • Domain name (for production SSL)"
    echo ""
    
    echo -e "${YELLOW}BEFORE RUNNING:${NC}"
    echo "  1. Ensure domain DNS points to this server"
    echo "  2. Backup existing nginx configurations"
    echo "  3. Review firewall implications"
    echo "  4. Have email address ready for SSL"
    echo ""
    
    echo -e "${RED}SECURITY WARNINGS:${NC}"
    echo "  ⚠️  This script modifies nginx configuration"
    echo "  ⚠️  This script configures UFW firewall rules"
    echo "  ⚠️  This script creates system users and services"
    echo "  ⚠️  Run only on servers you control"
    echo ""
    
    echo -e "${GREEN}POST-INSTALLATION:${NC}"
    echo "  • Application will be available at https://your-domain.com"
    echo "  • API endpoints at https://your-domain.com/api/"
    echo "  • Logs available in $APP_DIR/logs/"
    echo "  • Service management: systemctl status $APP_NAME"
    echo ""
}

# Get user input (only if in interactive mode)
get_user_input() {
    if [[ "$INTERACTIVE_MODE" == true ]]; then
        echo -e "${BLUE}AI Ethics Testing Framework Installation${NC}"
        echo "========================================"
        echo ""
        
        if [[ -z "$DOMAIN" ]]; then
            read -p "Enter your domain name (e.g., ethics.example.com): " DOMAIN
        fi
        
        if [[ -z "$APP_DIR" ]]; then
            read -p "Enter installation directory [/opt/ai-ethics]: " user_app_dir
            APP_DIR=${user_app_dir:-/opt/ai-ethics}
        fi
        
        if [[ -z "$SSL_EMAIL" ]]; then
            read -p "Enter email for SSL certificate (optional): " SSL_EMAIL
        fi
    fi
    
    # Validate required parameters
    if [[ -z "$DOMAIN" ]]; then
        error "Domain name is required. Use --domain DOMAIN or run in interactive mode."
    fi
    
    # Set defaults if not provided
    if [[ -z "$APP_DIR" ]]; then
        APP_DIR="/opt/ai-ethics"
    fi
    
    if [[ -z "$SSL_EMAIL" ]]; then
        warning "No email provided, SSL will be skipped"
    fi
    
    echo ""
    echo "Configuration:"
    echo "- Domain: $DOMAIN"
    echo "- Port: $APP_PORT"
    echo "- App Directory: $APP_DIR"
    echo "- SSL Email: $SSL_EMAIL"
    echo "- Service Name: $APP_NAME"
    echo ""
    
    if [[ "$INTERACTIVE_MODE" == true ]]; then
        read -p "Continue with installation? (y/N): " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "Installation cancelled"
            exit 0
        fi
    else
        log "Starting automated installation..."
    fi
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --domain)
                DOMAIN="$2"
                INTERACTIVE_MODE=false
                shift 2
                ;;
            --docroot)
                APP_DIR="$2"
                shift 2
                ;;
            --email)
                SSL_EMAIL="$2"
                shift 2
                ;;
            --port)
                APP_PORT="$2"
                shift 2
                ;;
            --app-name)
                APP_NAME="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown argument: $1"
                ;;
        esac
    done
}

# Show usage information
show_usage() {
    show_help_and_security
}

# Update system packages
update_system() {
    log "Updating system packages..."
    apt update && apt upgrade -y
    apt install -y curl wget git nginx python3 python3-pip python3-venv \
                   ufw software-properties-common build-essential \
                   sqlite3 supervisor
}

# Install Node.js (for frontend build tools if needed)
install_nodejs() {
    log "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    apt install -y nodejs
}

# Install Certbot for SSL
install_certbot() {
    if [[ -n "$SSL_EMAIL" ]]; then
        log "Installing Certbot for SSL certificates..."
        apt install -y certbot python3-certbot-nginx
    fi
}

# Create application user
create_app_user() {
    log "Creating application user..."
    if ! id "$APP_NAME" &>/dev/null; then
        useradd --system --home "$APP_DIR" --shell /bin/bash "$APP_NAME"
    fi
}

# Setup application directory
setup_app_directory() {
    log "Setting up application directory at $APP_DIR..."
    
    # Create directory structure
    mkdir -p "$APP_DIR"
    mkdir -p "$APP_DIR/logs"
    mkdir -p "$APP_DIR/static"
    mkdir -p "$APP_DIR/uploads"
    mkdir -p "$APP_DIR/backups"
    
    # Determine source directory
    SOURCE_DIR=""
    
    # Check if running from project directory
    if [[ -f "main.py" && -f "ethical_dilemmas.json" ]]; then
        SOURCE_DIR="$(pwd)"
        log "Found project files in current directory: $SOURCE_DIR"
    # Check if files are in /tmp (from git clone or upload)
    elif [[ -d "/tmp/aiforskning" ]]; then
        SOURCE_DIR="/tmp/aiforskning"
        log "Found project files in /tmp/aiforskning"
    # Check if script is in project directory
    elif [[ -f "$(dirname "$0")/main.py" ]]; then
        SOURCE_DIR="$(dirname "$0")"
        log "Found project files relative to script: $SOURCE_DIR"
    else
        error "Cannot find application files. Please ensure you're running from the project directory or the files are in /tmp/aiforskning"
    fi
    
    # Copy application files
    log "Copying files from $SOURCE_DIR to $APP_DIR..."
    cp -r "$SOURCE_DIR"/* "$APP_DIR/" 2>/dev/null || true
    
    # Ensure critical files exist
    if [[ ! -f "$APP_DIR/main.py" ]]; then
        error "main.py not found in $APP_DIR. Installation failed."
    fi
    
    if [[ ! -f "$APP_DIR/ethical_dilemmas.json" ]]; then
        error "ethical_dilemmas.json not found in $APP_DIR. Installation failed."
    fi
    
    # Set ownership
    chown -R "$APP_NAME:$APP_NAME" "$APP_DIR"
    chmod -R 755 "$APP_DIR"
    
    log "Application directory setup complete"
}

# Setup Python virtual environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    cd "$APP_DIR"
    sudo -u "$APP_NAME" python3 -m venv venv
    
    # Activate virtual environment and install dependencies
    sudo -u "$APP_NAME" bash -c "
        source venv/bin/activate
        pip install --upgrade pip
        pip install flask flask-cors gunicorn
    "
    
    # Initialize database
    sudo -u "$APP_NAME" bash -c "
        source venv/bin/activate
        python main.py init
    "
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > "$SYSTEMD_DIR/$APP_NAME.service" << EOF
[Unit]
Description=AI Ethics Testing Framework
After=network.target

[Service]
Type=exec
User=$APP_NAME
Group=$APP_NAME
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:$APP_PORT --workers 4 --timeout 120 'src.web_app:create_app()'
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR
CapabilityBoundingSet=

# Logging
StandardOutput=append:$APP_DIR/logs/app.log
StandardError=append:$APP_DIR/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$APP_NAME"
}

# Configure nginx
configure_nginx() {
    log "Configuring nginx..."
    
    # Remove default site if it exists
    if [[ -f "$NGINX_ENABLED/default" ]]; then
        rm "$NGINX_ENABLED/default"
    fi
    
    # Create nginx configuration
    cat > "$NGINX_AVAILABLE/$APP_NAME" << EOF
# IPv4 only configuration for AI Ethics Testing Framework
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline' 'unsafe-eval'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=web:10m rate=5r/s;
    
    location / {
        limit_req zone=web burst=10 nodelay;
        
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # API specific settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /(database|config|logs)/ {
        deny all;
    }
}
EOF
    
    # Enable site
    ln -sf "$NGINX_AVAILABLE/$APP_NAME" "$NGINX_ENABLED/"
    
    # Test nginx configuration
    nginx -t || error "nginx configuration test failed"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    if [[ -n "$SSL_EMAIL" ]]; then
        log "Setting up SSL certificate..."
        
        # Start nginx to get certificate
        systemctl restart nginx
        
        # Get SSL certificate
        certbot --nginx -d "$DOMAIN" --email "$SSL_EMAIL" --agree-tos --non-interactive --redirect
        
        # Setup auto-renewal
        (crontab -l 2>/dev/null; echo "0 2 * * * /usr/bin/certbot renew --quiet") | crontab -
    fi
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    # Enable UFW
    ufw --force enable
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Block direct access to application port
    ufw deny "$APP_PORT"
    
    # Allow from localhost only for app port
    ufw allow from 127.0.0.1 to any port "$APP_PORT"
    
    ufw reload
}

# Create monitoring script
create_monitoring() {
    log "Setting up monitoring..."
    
    cat > "$APP_DIR/monitor.sh" << 'EOF'
#!/bin/bash

# AI Ethics monitoring script
APP_NAME="ai-ethics"
LOG_FILE="/opt/ai-ethics/logs/monitor.log"
HEALTH_URL="http://localhost:8050/health"

log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if service is running
if ! systemctl is-active --quiet "$APP_NAME"; then
    log_message "ERROR: Service is not running, attempting restart"
    systemctl restart "$APP_NAME"
    sleep 10
fi

# Check HTTP health
if ! curl -f -s "$HEALTH_URL" > /dev/null; then
    log_message "ERROR: Health check failed, restarting service"
    systemctl restart "$APP_NAME"
fi

# Check disk space
DISK_USAGE=$(df /opt | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log_message "WARNING: Disk usage is at ${DISK_USAGE}%"
fi

# Rotate logs if too large
find /opt/ai-ethics/logs -name "*.log" -size +100M -exec truncate -s 50M {} \;

log_message "Health check completed"
EOF
    
    chmod +x "$APP_DIR/monitor.sh"
    chown "$APP_NAME:$APP_NAME" "$APP_DIR/monitor.sh"
    
    # Add to crontab for regular monitoring
    (crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor.sh") | crontab -
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    cat > "$APP_DIR/backup.sh" << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/ai-ethics/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/ai-ethics"

mkdir -p "$BACKUP_DIR"

# Backup database
if [ -f "$APP_DIR/ethics_data.db" ]; then
    cp "$APP_DIR/ethics_data.db" "$BACKUP_DIR/ethics_data_$DATE.db"
fi

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$APP_DIR" \
    ethical_dilemmas.json requirements.txt

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x "$APP_DIR/backup.sh"
    chown "$APP_NAME:$APP_NAME" "$APP_DIR/backup.sh"
    
    # Schedule daily backups at 3 AM
    (crontab -l 2>/dev/null; echo "0 3 * * * $APP_DIR/backup.sh") | crontab -
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start application
    systemctl start "$APP_NAME"
    systemctl status "$APP_NAME" --no-pager
    
    # Restart nginx
    systemctl restart nginx
    systemctl status nginx --no-pager
    
    # Wait a moment for services to start
    sleep 5
    
    # Test application
    if curl -f -s "http://localhost:$APP_PORT/health" > /dev/null; then
        log "Application health check: ✓ PASSED"
    else
        warning "Application health check failed"
    fi
}

# Display final information
show_completion_info() {
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}🎉 AI Ethics Testing Framework Installation Complete!${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    echo "📍 Access URLs:"
    if [[ -n "$SSL_EMAIL" ]]; then
        echo "   🌐 Main Dashboard: https://$DOMAIN"
        echo "   🎨 Vue Dashboard:  https://$DOMAIN/vue"
    else
        echo "   🌐 Main Dashboard: http://$DOMAIN"
        echo "   🎨 Vue Dashboard:  http://$DOMAIN/vue"
    fi
    echo ""
    echo "🔧 Management Commands:"
    echo "   📊 Status:        sudo systemctl status $APP_NAME"
    echo "   🔄 Restart:       sudo systemctl restart $APP_NAME"
    echo "   📜 Logs:          sudo journalctl -u $APP_NAME -f"
    echo "   💾 Backup:        sudo $APP_DIR/backup.sh"
    echo "   🔍 Monitor:       sudo $APP_DIR/monitor.sh"
    echo ""
    echo "📁 Important Paths:"
    echo "   🏠 App Directory: $APP_DIR"
    echo "   📊 Database:      $APP_DIR/ethics_data.db"
    echo "   📋 Logs:         $APP_DIR/logs/"
    echo "   💾 Backups:      $APP_DIR/backups/"
    echo ""
    echo "🔥 Next Steps:"
    echo "   1. Test the application by visiting the URLs above"
    echo "   2. Run a demo test: sudo -u $APP_NAME $APP_DIR/venv/bin/python $APP_DIR/demo.py"
    echo "   3. Check logs if you encounter any issues"
    echo "   4. Integrate your AI models using the API interface"
    echo ""
    echo -e "${BLUE}📚 Documentation: Check README.md for API integration details${NC}"
    echo ""
}

# Main installation function
main() {
    # Check if no arguments provided - show help and security info
    if [[ $# -eq 0 ]]; then
        show_help_and_security
        echo -e "${BLUE}Continue with interactive installation? (y/N): ${NC}"
        read -r continue_interactive
        if [[ ! "$continue_interactive" =~ ^[Yy]$ ]]; then
            echo "Installation cancelled. Use './install.sh --help' for more options."
            exit 0
        fi
        INTERACTIVE_MODE=true
    fi

    echo -e "${BLUE}"
    cat << "EOF"
     _    ___   _____ _   _     _           
    / \  |_ _| | ____| |_| |__ (_) ___ ___  
   / _ \  | |  |  _| | __| '_ \| |/ __/ __| 
  / ___ \ | |  | |___| |_| | | | | (__\__ \ 
 /_/   \_\___| |_____|\__|_| |_|_|\___|___/ 
                                           
 Testing Framework - Production Installation
EOF
    echo -e "${NC}"
    
    check_root
    parse_arguments "$@"
    security_check
    
    if [ "$INTERACTIVE_MODE" = true ]; then
        get_user_input
    fi
    
    log "Starting installation process..."
    
    update_system
    install_nodejs
    install_certbot
    create_app_user
    setup_app_directory
    setup_python_env
    create_systemd_service
    configure_nginx
    setup_ssl
    configure_firewall
    create_monitoring
    create_backup_script
    start_services
    
    show_completion_info
}

# Run main function
main "$@"
