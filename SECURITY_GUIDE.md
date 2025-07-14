# 🔒 AI Ethics Testing Framework - Security Installation Guide

## Overview
The AI Ethics Testing Framework now includes comprehensive security checks and guided installation to ensure safe deployment on production servers.

## Security Features Added

### 🛡️ **Pre-Installation Security Validation**
- **System State Analysis**: Checks for existing nginx, SSL certificates, port conflicts
- **Resource Validation**: Verifies available disk space and system requirements  
- **Environment Detection**: Identifies production vs development environments
- **Warning System**: Clear alerts for potential conflicts or security implications

### 🔐 **Security-First Installation Process**
- **UFW Firewall**: Automatically configures firewall rules (SSH, HTTP, HTTPS only)
- **SSL/TLS Encryption**: Let's Encrypt certificates with auto-renewal
- **Dedicated User**: Creates restricted system user with no shell access
- **File Permissions**: Sets minimal required permissions for all components
- **IPv4-Only**: Disables IPv6 to reduce attack surface

### ⚠️ **Safety Mechanisms**
- **Interactive Confirmation**: Requires explicit user consent for risky operations
- **Dry Run Validation**: Syntax checking before execution
- **Backup Integration**: Automated backup of existing configurations
- **Monitoring Setup**: Includes security monitoring and alerting

## Usage Examples

### 📋 **Show Security Help (Default Behavior)**
```bash
./install.sh
```
This now displays comprehensive security information and installation options.

### 🚀 **Production Installation**
```bash
sudo ./install.sh --domain ethics.example.com --email admin@example.com
```

### 🏠 **Custom Directory**
```bash  
sudo ./install.sh --domain ethics.local --docroot /var/www/ethics
```

### 🔧 **Development Setup**
```bash
sudo ./install.sh --domain localhost --port 8050
```

### ❓ **Get Help**
```bash
./install.sh --help
./install.sh -h
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--domain DOMAIN` | Domain name (required for production) | `--domain ethics.example.com` |
| `--docroot PATH` | Installation directory | `--docroot /var/www/ethics` |
| `--email EMAIL` | Email for SSL certificates | `--email admin@example.com` |
| `--port PORT` | Application port (default: 8050) | `--port 8080` |
| `--app-name NAME` | Service name (default: ai-ethics) | `--app-name my-ethics` |
| `--help, -h` | Show comprehensive help | `--help` |

## Security Warnings Displayed

The installation script now provides clear warnings about:
- ⚠️ nginx configuration modifications
- ⚠️ UFW firewall rule changes  
- ⚠️ System user and service creation
- ⚠️ SSL certificate requests
- ⚠️ File permission changes

## Before Running Installation

1. **DNS Configuration**: Ensure domain DNS points to your server
2. **Backup Existing Configs**: Back up nginx and other configurations
3. **Review Firewall Impact**: Understand which ports will be opened/closed
4. **Email Access**: Have a valid email for SSL certificate registration
5. **System Resources**: Ensure 1GB+ disk space and Ubuntu 18.04+

## Post-Installation Security

After installation, the system provides:
- **HTTPS-Only Access**: All traffic encrypted via SSL
- **Restricted Permissions**: Application runs as dedicated user
- **Firewall Protection**: Only necessary ports exposed
- **Monitoring**: Security alerts and log monitoring
- **Backup System**: Automated backups of data and configs

## Emergency Commands

```bash
# Check service status
sudo systemctl status ai-ethics

# View logs
sudo journalctl -u ai-ethics -f

# Stop service
sudo systemctl stop ai-ethics

# Check firewall status
sudo ufw status

# Check SSL certificate status
sudo certbot certificates
```

## Testing the Installation

Use the included test script to validate the installation:
```bash
python test_install.py
```

This validates:
- ✅ Installation script syntax and security features
- ✅ Framework component availability  
- ✅ Python syntax validation
- ✅ Example command testing

## Support

The installation script now provides comprehensive help and security guidance by default. Simply run `./install.sh` to see all available options and security considerations.
