#!/bin/bash

# Script to diagnose and fix nginx redirect issues
# Specifically for the problem where all domains redirect to skydash.no

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to backup nginx configuration
backup_nginx() {
    print_status "Creating backup of nginx configuration..."
    
    BACKUP_DIR="/root/nginx-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    cp -r /etc/nginx/sites-available "$BACKUP_DIR/"
    cp -r /etc/nginx/sites-enabled "$BACKUP_DIR/"
    cp /etc/nginx/nginx.conf "$BACKUP_DIR/"
    
    print_success "Backup created at: $BACKUP_DIR"
}

# Function to diagnose nginx configuration
diagnose_nginx() {
    print_status "Diagnosing nginx configuration..."
    
    echo "=== Current nginx sites-enabled ==="
    ls -la /etc/nginx/sites-enabled/
    echo
    
    echo "=== Current nginx sites-available ==="
    ls -la /etc/nginx/sites-available/
    echo
    
    echo "=== Checking for skydash.no references ==="
    grep -r "skydash.no" /etc/nginx/ 2>/dev/null || echo "No direct skydash.no references found"
    echo
    
    echo "=== Checking all server_name directives ==="
    grep -r "server_name" /etc/nginx/sites-available/ 2>/dev/null || echo "No server_name directives found"
    echo
    
    echo "=== Checking for default_server directives ==="
    grep -r "default_server" /etc/nginx/ 2>/dev/null || echo "No default_server directives found"
    echo
    
    echo "=== Checking nginx test ==="
    nginx -t
    echo
}

# Function to fix the nginx configuration
fix_nginx_config() {
    print_status "Fixing nginx configuration..."
    
    # Remove problematic default configurations
    print_status "Removing default nginx site..."
    rm -f /etc/nginx/sites-enabled/default
    rm -f /etc/nginx/sites-enabled/000-default
    
    # Remove any skydash.no configurations
    print_status "Removing any skydash.no configurations..."
    find /etc/nginx/sites-available/ -name "*skydash*" -delete 2>/dev/null || true
    find /etc/nginx/sites-enabled/ -name "*skydash*" -delete 2>/dev/null || true
    
    # Ensure only testsider.no is enabled
    print_status "Ensuring testsider.no configuration is correct..."
    
    if [[ ! -f "/etc/nginx/sites-available/testsider.no" ]]; then
        print_warning "testsider.no configuration not found, creating it..."
        
        cat > "/etc/nginx/sites-available/testsider.no" << 'EOF'
server {
    listen 80;
    server_name testsider.no www.testsider.no;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
    
    # Static files
    location /static {
        proxy_pass http://127.0.0.1:5000/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    fi
    
    # Enable testsider.no site
    ln -sf "/etc/nginx/sites-available/testsider.no" "/etc/nginx/sites-enabled/"
    
    # Create a catch-all server block to prevent unwanted redirects
    print_status "Creating catch-all server block..."
    cat > "/etc/nginx/sites-available/000-catch-all" << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    # Return 444 (no response) for undefined hosts
    return 444;
}
EOF
    
    ln -sf "/etc/nginx/sites-available/000-catch-all" "/etc/nginx/sites-enabled/000-catch-all"
    
    # Test nginx configuration
    print_status "Testing nginx configuration..."
    if nginx -t; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration has errors"
        return 1
    fi
    
    # Reload nginx
    print_status "Reloading nginx..."
    systemctl reload nginx
    
    print_success "Nginx configuration fixed!"
}

# Function to verify the fix
verify_fix() {
    print_status "Verifying the fix..."
    
    echo "=== Final nginx sites-enabled ==="
    ls -la /etc/nginx/sites-enabled/
    echo
    
    echo "=== Testing local requests ==="
    echo "Testing testsider.no:"
    curl -H "Host: testsider.no" http://localhost/health 2>/dev/null || echo "Could not reach testsider.no"
    
    echo "Testing unknown domain:"
    curl -H "Host: unknown.domain" http://localhost/ 2>/dev/null || echo "Unknown domain properly blocked (expected)"
    
    print_success "Fix verification complete"
}

# Main execution
main() {
    echo "=== Nginx Redirect Fix Script ==="
    echo "This script will fix nginx configuration issues that cause"
    echo "all domains to redirect to skydash.no"
    echo
    
    check_root
    
    read -p "Do you want to proceed? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    
    backup_nginx
    echo
    
    print_status "Phase 1: Diagnosis"
    diagnose_nginx
    echo
    
    print_status "Phase 2: Fixing configuration"
    if fix_nginx_config; then
        echo
        print_status "Phase 3: Verification"
        verify_fix
        echo
        print_success "All done! Your nginx should now serve testsider.no correctly."
        print_status "If you had SSL certificates, you may need to run:"
        print_status "certbot --nginx -d testsider.no -d www.testsider.no"
    else
        print_error "Configuration fix failed. Check the backup at nginx-backup-*"
        exit 1
    fi
}

# Run the main function
main "$@"
