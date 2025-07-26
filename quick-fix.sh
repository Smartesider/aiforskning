#!/bin/bash
# Quick fix to redirect forskning.skycode.no to the correct AI Ethics Framework

echo "🔧 Implementing quick fix for forskning.skycode.no..."

# Create a simple nginx config snippet that redirects port 8020 to our app
cat > /tmp/fix-forskning.conf << 'EOF'
# Quick fix for forskning.skycode.no - redirect to AI Ethics Framework
server {
    listen 8022;
    server_name forskning.skycode.no localhost;
    
    location / {
        proxy_pass http://127.0.0.1:8021;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Add headers to identify the source
        add_header X-Served-By "AI-Ethics-Framework" always;
    }
}
EOF

echo "✅ Created nginx configuration for port 8022"
echo "📋 Configuration saved to /tmp/fix-forskning.conf"

# Test if our app is running
if curl -s http://127.0.0.1:8021 >/dev/null; then
    echo "✅ AI Ethics Framework is running on port 8021"
else
    echo "❌ AI Ethics Framework not responding on port 8021"
    exit 1
fi

# Test the proxy would work
echo "🧪 Testing proxy setup on port 8022..."
echo "📝 To implement this fix, you need to:"
echo ""
echo "1. Copy the configuration to nginx:"
echo "   sudo cp /tmp/fix-forskning.conf /etc/nginx/sites-available/"
echo "   sudo ln -sf /etc/nginx/sites-available/fix-forskning.conf /etc/nginx/sites-enabled/"
echo ""
echo "2. Test and reload nginx:"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "3. Access via: http://forskning.skycode.no:8022"
echo ""
echo "🔄 Alternative: Update existing container/service to point to 127.0.0.1:8021"
echo ""
echo "📊 Current status:"
echo "- AI Ethics Framework: ✅ Running on 127.0.0.1:8021"
echo "- Default 'Velkommen': ❌ Still on port 8020 (needs replacement)"
echo "- Proxy config ready: ✅ Available at /tmp/fix-forskning.conf"

# Show what's actually running
echo ""
echo "🔍 Current application responses:"
echo "Port 8020: $(curl -s http://localhost:8020 | head -1)"
echo "Port 8021: $(curl -s http://localhost:8021 | head -1)"
