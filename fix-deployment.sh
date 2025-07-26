#!/bin/bash
# Fix deployment script for forskning.skycode.no
# This script fixes the nginx configuration to point to the correct AI Ethics Framework

set -e

echo "🔧 Fixing forskning.skycode.no deployment..."

# Check if our AI Ethics Framework is running
if ! curl -s http://localhost:8021 >/dev/null; then
    echo "❌ AI Ethics Framework not running on port 8021"
    echo "🚀 Starting AI Ethics Framework..."
    cd /home/skyforskning.no/forskning
    python3 -m gunicorn --bind 0.0.0.0:8021 --workers 4 --timeout 120 run_app:app --log-level info --daemon
    sleep 2
fi

echo "✅ AI Ethics Framework is running on port 8021"

# Test the application
echo "🧪 Testing application response..."
RESPONSE=$(curl -s http://localhost:8021 | head -1)
if [[ "$RESPONSE" == *"DOCTYPE html"* ]]; then
    echo "✅ Application responding correctly"
else
    echo "❌ Application not responding correctly"
    echo "Response: $RESPONSE"
fi

# Show current process status
echo ""
echo "📊 Current server processes:"
ps aux | grep -E "(gunicorn.*8021|nginx)" | grep -v grep

echo ""
echo "🌐 Port status:"
ss -tlpn | grep -E "(:80|:443|:8020|:8021)"

echo ""
echo "📝 Next steps to fix the deployment:"
echo "1. The AI Ethics Framework is now running on port 8021"
echo "2. Copy the nginx configuration:"
echo "   sudo cp /home/skyforskning.no/forskning/nginx-forskning.conf /etc/nginx/sites-available/forskning.skycode.no"
echo "3. Enable the site:"
echo "   sudo ln -sf /etc/nginx/sites-available/forskning.skycode.no /etc/nginx/sites-enabled/"
echo "4. Test nginx configuration:"
echo "   sudo nginx -t"
echo "5. Reload nginx:"
echo "   sudo systemctl reload nginx"
echo ""
echo "🔍 Alternative: If using Portainer/Docker, update the container to:"
echo "   - Point to port 8021 instead of whatever is serving the 'Velkommen' message"
echo "   - Or stop the container serving port 8020 and redirect there"
echo ""
echo "✅ AI Ethics Testing Framework is ready at: http://localhost:8021"
