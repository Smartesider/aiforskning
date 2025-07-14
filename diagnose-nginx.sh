#!/bin/bash

# Quick nginx diagnostic script
# Run this to see what's causing all domains to redirect to skydash.no

echo "=== Nginx Redirect Diagnostic ==="
echo

echo "1. Current enabled sites:"
ls -la /etc/nginx/sites-enabled/
echo

echo "2. All server_name directives:"
grep -r "server_name" /etc/nginx/sites-available/ 2>/dev/null | head -20
echo

echo "3. Looking for skydash.no references:"
grep -r "skydash" /etc/nginx/ 2>/dev/null || echo "No skydash references found in nginx config"
echo

echo "4. Looking for default_server directives:"
grep -r "default_server" /etc/nginx/ 2>/dev/null || echo "No default_server directives found"
echo

echo "5. Looking for return/redirect directives:"
grep -r "return\|redirect" /etc/nginx/sites-available/ 2>/dev/null | head -10
echo

echo "6. Current nginx status:"
systemctl status nginx --no-pager -l
echo

echo "7. Recent nginx error logs:"
tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No error log found"
echo

echo "8. Testing nginx configuration:"
nginx -t
echo

echo "=== Diagnostic Complete ==="
echo "Look for:"
echo "- Multiple sites in sites-enabled"
echo "- default_server on wrong site"
echo "- Redirect rules to skydash.no"
echo "- SSL configuration issues"
