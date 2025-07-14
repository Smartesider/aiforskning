#!/bin/bash

# Enhanced nginx diagnostic script
# Run this to see what's causing all domains to redirect to skydash.no

echo "=== Enhanced Nginx Redirect Diagnostic ==="
echo

echo "1. Current enabled sites:"
ls -la /etc/nginx/sites-enabled/
echo

echo "2. All server_name directives with their files:"
for site in /etc/nginx/sites-available/*; do
    if [[ -f "$site" ]]; then
        site_name=$(basename "$site")
        domains=$(grep -H "server_name" "$site" 2>/dev/null | head -3)
        if [[ -n "$domains" ]]; then
            echo "  === $site_name ==="
            echo "$domains"
        fi
    fi
done
echo

echo "3. Looking for default_server directives:"
grep -r "default_server" /etc/nginx/sites-enabled/ 2>/dev/null || echo "No default_server directives found in enabled sites"
echo

echo "4. Looking for catch-all server names (_):"
grep -r "server_name.*_" /etc/nginx/sites-enabled/ 2>/dev/null || echo "No catch-all server names found"
echo

echo "5. Looking for skydash.no references:"
grep -r "skydash" /etc/nginx/ 2>/dev/null || echo "No skydash references found in nginx config"
echo

echo "6. Looking for redirect rules:"
echo "  === HTTP redirects ==="
grep -r "return.*30[1-8]" /etc/nginx/sites-available/ 2>/dev/null | head -10
echo "  === Rewrite redirects ==="
grep -r "rewrite.*redirect" /etc/nginx/sites-available/ 2>/dev/null | head -10
echo

echo "7. SSL configuration status:"
for site in /etc/nginx/sites-enabled/*; do
    if [[ -f "$site" ]]; then
        site_name=$(basename "$site")
        if grep -q "listen.*443.*ssl" "$site" 2>/dev/null; then
            echo "  $site_name: HTTPS enabled"
        else
            echo "  $site_name: HTTP only"
        fi
    fi
done
echo

echo "8. Let's Encrypt certificates:"
if [[ -d "/etc/letsencrypt/live" ]]; then
    ls -la /etc/letsencrypt/live/
else
    echo "No Let's Encrypt certificates found"
fi
echo

echo "9. Current nginx status:"
systemctl status nginx --no-pager -l
echo

echo "10. Recent nginx error logs:"
tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No error log found"
echo

echo "11. Testing nginx configuration:"
nginx -t
echo

echo "=== Diagnostic Complete ==="
echo "POTENTIAL ISSUES TO LOOK FOR:"
echo "- Multiple sites with default_server directive"
echo "- Sites with server_name _ (catch-all) that redirect to skydash.no"
echo "- SSL redirects that might be interfering"
echo "- Missing or misconfigured testsider.no virtual host"
echo "- Conflicting location blocks or proxy_pass directives"
