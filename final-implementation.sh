#!/bin/bash
# ENDELIG IMPLEMENTERING: Erstatt statisk innhold på forskning.skycode.no

echo "🚀 ENDELIG IMPLEMENTERING - AI Ethics Framework"
echo "🎯 Erstatter 'Velkommen til skyforskning' med AI Ethics Testing Framework"

# Start AI Ethics Framework på port som garantert fungerer
cd /home/skyforskning.no/forskning

# Stopp alle eksisterende instanser
pkill -f "run_app:app" 2>/dev/null || true

# Start på port 8021 (som vi vet fungerer)
python3 -m gunicorn --bind 127.0.0.1:8021 --workers 4 --timeout 120 run_app:app --daemon

sleep 3

# Test at det fungerer
if curl -s http://localhost:8021 | grep -q "DOCTYPE"; then
    echo "✅ AI Ethics Framework kjører på port 8021"
else
    echo "❌ Feil ved oppstart"
    exit 1
fi

echo ""
echo "🔧 IMPLEMENTERER NGINX PROXY..."

# Opprett nginx konfigurasjon som erstatter statisk innhold
cat > /tmp/ai-ethics-nginx.conf << 'EOF'
server {
    listen 8020;
    server_name forskning.skycode.no localhost _;
    
    # Erstatt all statisk innhold med proxy til AI Ethics Framework
    location / {
        proxy_pass http://127.0.0.1:8021;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Headers for å identifisere at dette er AI Ethics Framework
        add_header X-Powered-By "AI-Ethics-Testing-Framework" always;
        add_header X-Source "AI-Dashboard-Replacement" always;
        
        # Disable caching
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        expires -1;
    }
}

# HTTPS version (hvis SSL er aktivert)
server {
    listen 443 ssl http2;
    server_name forskning.skycode.no;
    
    # SSL konfigurasjon
    ssl_certificate /etc/letsencrypt/live/forskning.skycode.no/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forskning.skycode.no/privkey.pem;
    
    # Same proxy configuration
    location / {
        proxy_pass http://127.0.0.1:8021;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        add_header X-Powered-By "AI-Ethics-Testing-Framework" always;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
EOF

echo "✅ Nginx konfigurasjon opprettet"
echo ""
echo "🚀 FOR Å FULLFØRE (kjør denne kommandoen):"
echo ""
echo "sudo cp /tmp/ai-ethics-nginx.conf /etc/nginx/sites-available/ai-ethics-forskning.conf && sudo ln -sf /etc/nginx/sites-available/ai-ethics-forskning.conf /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "ELLER kjør hver kommando separat:"
echo "1. sudo cp /tmp/ai-ethics-nginx.conf /etc/nginx/sites-available/ai-ethics-forskning.conf"
echo "2. sudo ln -sf /etc/nginx/sites-available/ai-ethics-forskning.conf /etc/nginx/sites-enabled/"
echo "3. sudo nginx -t"
echo "4. sudo systemctl reload nginx"
echo ""

# Vis status
echo "📊 NÅVÆRENDE STATUS:"
echo "✅ AI Ethics Framework: http://localhost:8021 (klar)"
echo "🔧 Nginx konfigurasjon: /tmp/ai-ethics-nginx.conf (klar)"
echo "⏳ forskning.skycode.no: Venter på nginx oppdatering"

echo ""
echo "🎯 ETTER NGINX OPPDATERING:"
echo "https://forskning.skycode.no → AI Ethics Testing Dashboard"
echo "Statisk 'Velkommen til skyforskning' → Erstattet! ✅"

echo ""
echo "🧪 TEST LOKAL TILGANG NÅ:"
echo "http://localhost:8021 - Se AI Ethics Framework"

# Test og vis innhold
echo ""
echo "📋 FORHÅNDSVISNING AV INNHOLD:"
TITLE=$(curl -s http://localhost:8021 | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g' 2>/dev/null || echo "AI Ethics Testing Framework")
echo "Sidetittel: $TITLE"
echo "Status: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8021 2>/dev/null)"
