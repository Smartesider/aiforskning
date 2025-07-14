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

# Function to identify conflicting hosts
identify_conflicting_hosts() {
    print_status "Identifying conflicting virtual hosts..."
    
    # Find hosts with default_server directive or catch-all configurations
    CONFLICTING_HOSTS=()
    CATCH_ALL_HOSTS=()
    
    for site in /etc/nginx/sites-enabled/*; do
        if [[ -f "$site" ]]; then
            site_name=$(basename "$site")
            
            # Check for default_server directive
            if grep -q "default_server" "$site"; then
                CONFLICTING_HOSTS+=("$site_name")
                print_warning "Found default_server in: $site_name"
            fi
            
            # Check for catch-all server_name (_, empty, or wildcard)
            if grep -E "server_name\s+(_|;|\*)" "$site" > /dev/null; then
                CATCH_ALL_HOSTS+=("$site_name")
                print_warning "Found catch-all server_name in: $site_name"
            fi
            
            # Check for specific problematic redirects
            if grep -q "skydash.no" "$site"; then
                print_warning "Found skydash.no reference in: $site_name"
            fi
        fi
    done
    
    echo "CONFLICTING_HOSTS: ${CONFLICTING_HOSTS[*]}"
    echo "CATCH_ALL_HOSTS: ${CATCH_ALL_HOSTS[*]}"
}

# Function to preserve SSL certificates and redirects
preserve_ssl_configurations() {
    print_status "Preserving SSL certificates and redirects..."
    
    # Check for existing SSL configurations
    for site in /etc/nginx/sites-available/*; do
        if [[ -f "$site" ]]; then
            site_name=$(basename "$site")
            
            # Skip testsider.no as we'll handle it separately
            if [[ "$site_name" == "testsider.no" ]]; then
                continue
            fi
            
            # Check if this site has SSL configuration
            if grep -q "listen.*443.*ssl" "$site" || grep -q "ssl_certificate" "$site"; then
                print_status "Found SSL configuration in: $site_name"
                
                # Extract domain name
                DOMAIN=$(grep -oP 'server_name\s+\K[^;\s_*]+' "$site" | head -1 | grep -v '^$' || echo "")
                
                if [[ -n "$DOMAIN" && "$DOMAIN" != "_" ]]; then
                    print_status "Preserving SSL for domain: $DOMAIN"
                    
                    # Check if Let's Encrypt certificates exist
                    if [[ -d "/etc/letsencrypt/live/$DOMAIN" ]]; then
                        print_success "Let's Encrypt certificates found for $DOMAIN"
                        
                        # The configuration was already preserved in preserve_existing_hosts
                        # Just ensure SSL configuration is intact
                        if [[ -f "/etc/nginx/sites-available/$DOMAIN" ]]; then
                            # Verify SSL configuration is present
                            if ! grep -q "ssl_certificate" "/etc/nginx/sites-available/$DOMAIN"; then
                                print_warning "SSL configuration missing for $DOMAIN, you may need to run certbot again"
                            fi
                        fi
                    fi
                fi
            fi
        fi
    done
}

# Function to backup and preserve existing host configurations
preserve_existing_hosts() {
    print_status "Preserving existing host configurations..."
    
    # Create preservation directory
    PRESERVE_DIR="/etc/nginx/sites-preserved-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$PRESERVE_DIR"
    
    # Process each enabled site
    for site in /etc/nginx/sites-enabled/*; do
        if [[ -f "$site" ]]; then
            site_name=$(basename "$site")
            site_path="/etc/nginx/sites-available/$site_name"
            
            # Skip if it's testsider.no (we'll recreate this)
            if [[ "$site_name" == "testsider.no" ]]; then
                continue
            fi
            
            print_status "Processing existing host: $site_name"
            
            # Copy original configuration
            cp "$site_path" "$PRESERVE_DIR/$site_name.original" 2>/dev/null || true
            
            # Check if this host has problematic configurations
            if grep -q "default_server" "$site_path" || grep -E "server_name\s+(_|;|\*)" "$site_path" > /dev/null; then
                print_status "Fixing problematic configuration in: $site_name"
                
                # Create fixed version
                sed 's/default_server//g' "$site_path" > "$PRESERVE_DIR/$site_name.fixed"
                
                # Extract actual domain name if possible
                ACTUAL_DOMAIN=$(grep -oP 'server_name\s+\K[^;\s_*]+' "$site_path" | head -1 | grep -v '^$' || echo "")
                
                if [[ -n "$ACTUAL_DOMAIN" && "$ACTUAL_DOMAIN" != "_" ]]; then
                    print_status "Preserving host for domain: $ACTUAL_DOMAIN"
                    
                    # Create proper domain-specific configuration
                    cat > "/etc/nginx/sites-available/$ACTUAL_DOMAIN" << EOF
# Preserved configuration for $ACTUAL_DOMAIN
# Original from: $site_name
$(cat "$PRESERVE_DIR/$site_name.fixed")
EOF
                    
                    # Update server_name to be specific
                    sed -i "s/server_name.*_;/server_name $ACTUAL_DOMAIN www.$ACTUAL_DOMAIN;/" "/etc/nginx/sites-available/$ACTUAL_DOMAIN"
                    
                    # Enable the new configuration
                    ln -sf "/etc/nginx/sites-available/$ACTUAL_DOMAIN" "/etc/nginx/sites-enabled/$ACTUAL_DOMAIN"
                    
                    print_success "Preserved $ACTUAL_DOMAIN configuration"
                else
                    print_warning "Could not determine domain for $site_name, keeping as-is but removing default_server"
                    sed -i 's/default_server//g' "$site_path"
                fi
            else
                print_status "Host $site_name looks OK, preserving as-is"
            fi
        fi
    done
    
    print_success "Existing hosts preserved in: $PRESERVE_DIR"
}

# Function to fix the nginx configuration
fix_nginx_config() {
    print_status "Fixing nginx configuration..."
    
    # First identify and preserve existing configurations
    identify_conflicting_hosts
    preserve_existing_hosts
    preserve_ssl_configurations
    
    # Remove only the default nginx site (not custom sites)
    print_status "Removing default nginx site..."
    rm -f /etc/nginx/sites-enabled/default
    rm -f /etc/nginx/sites-enabled/000-default
    
    # DON'T remove skydash.no or other custom configurations
    # Instead, they were already preserved properly above
    print_status "Ensuring custom domains remain properly configured..."
    
    # Ensure testsider.no configuration is correct
    print_status "Creating/updating testsider.no configuration..."
    
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
    
    # Enable testsider.no site
    ln -sf "/etc/nginx/sites-available/testsider.no" "/etc/nginx/sites-enabled/"
    
    # Create a minimal catch-all ONLY if no other catch-all exists
    EXISTING_CATCHALL=$(find /etc/nginx/sites-enabled/ -exec grep -l "server_name.*_" {} \; 2>/dev/null | head -1)
    
    if [[ -z "$EXISTING_CATCHALL" ]]; then
        print_status "Creating minimal catch-all for undefined hosts..."
        cat > "/etc/nginx/sites-available/999-catch-undefined" << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    # Return 444 (no response) for truly undefined hosts
    # This only catches domains not handled by other vhosts
    return 444;
}
EOF
        ln -sf "/etc/nginx/sites-available/999-catch-undefined" "/etc/nginx/sites-enabled/999-catch-undefined"
    else
        print_status "Existing catch-all found at: $EXISTING_CATCHALL - not creating new one"
    fi
    
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
    
    echo "=== All configured domains ==="
    for site in /etc/nginx/sites-enabled/*; do
        if [[ -f "$site" ]]; then
            site_name=$(basename "$site")
            domains=$(grep -oP 'server_name\s+\K[^;]+' "$site" 2>/dev/null || echo "unknown")
            ssl_status="HTTP only"
            if grep -q "listen.*443.*ssl" "$site" 2>/dev/null; then
                ssl_status="HTTPS enabled"
            fi
            echo "  $site_name: $domains ($ssl_status)"
        fi
    done
    echo
    
    echo "=== Testing local requests ==="
    echo "Testing testsider.no:"
    curl -H "Host: testsider.no" http://localhost/health 2>/dev/null || echo "Could not reach testsider.no"
    
    echo "Testing unknown domain:"
    curl -H "Host: unknown.domain" http://localhost/ 2>/dev/null || echo "Unknown domain properly blocked (expected)"
    
    echo "=== SSL Certificate Status ==="
    for domain_dir in /etc/letsencrypt/live/*/; do
        if [[ -d "$domain_dir" ]]; then
            domain=$(basename "$domain_dir")
            echo "  SSL certificates available for: $domain"
        fi
    done
    
    print_success "Fix verification complete"
    print_status "Summary:"
    echo "  • Existing domains preserved with their SSL certificates"
    echo "  • testsider.no configured and enabled"
    echo "  • Default server catch-all configured to prevent unwanted redirects"
    echo "  • All configurations tested and validated"
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
