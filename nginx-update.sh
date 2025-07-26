#!/bin/bash
# Nginx konfigurasjon for å proxy forskning.skycode.no til AI Ethics Framework

echo "🔧 Oppdaterer nginx for å peke til AI Ethics Framework"

# Start vår app hvis den ikke kjører
if ! curl -s http://localhost:8021 >/dev/null; then
    echo "🚀 Starter AI Ethics Framework på port 8021..."
    cd /home/skyforskning.no/forskning
    python3 -m gunicorn --bind 127.0.0.1:8021 --workers 4 --timeout 120 run_app:app --daemon
    sleep 3
fi

echo "✅ AI Ethics Framework kjører på port 8021"

# Opprett nginx site konfigurasjon
cat > /tmp/forskning-skycode.conf << 'EOF'
# Konfigurasjon for forskning.skycode.no
# Proxy til AI Ethics Testing Framework

server {
    listen 8020;
    server_name forskning.skycode.no localhost;
    
    # Proxy alle forespørsler til AI Ethics Framework
    location / {
        proxy_pass http://127.0.0.1:8021;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        
        # Headers for identifikasjon
        add_header X-Served-By "AI-Ethics-Framework" always;
        add_header X-Proxy-Cache "BYPASS" always;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8021/health;
        access_log off;
    }
}

# HTTPS konfigurasjon (hvis SSL er aktivert)
server {
    listen 443 ssl http2;
    server_name forskning.skycode.no;
    
    # SSL sertifikat (juster sti etter behov)
    ssl_certificate /etc/letsencrypt/live/forskning.skycode.no/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forskning.skycode.no/privkey.pem;
    
    # Samme proxy konfigurasjon som ovenfor
    location / {
        proxy_pass http://127.0.0.1:8021;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        add_header X-Served-By "AI-Ethics-Framework" always;
    }
}
EOF

echo "✅ Opprettet nginx konfigurasjon: /tmp/forskning-skycode.conf"

# Test konfigurasjonen
echo "🧪 Tester nginx konfigurasjon..."

# Kommandoer for implementering
echo ""
echo "🚀 IMPLEMENTERING:"
echo ""
echo "1. Kopier nginx konfigurasjon:"
echo "   sudo cp /tmp/forskning-skycode.conf /etc/nginx/sites-available/"
echo ""
echo "2. Aktiver konfigurasjonen:"
echo "   sudo ln -sf /etc/nginx/sites-available/forskning-skycode.conf /etc/nginx/sites-enabled/"
echo ""
echo "3. Test nginx konfigurasjon:"
echo "   sudo nginx -t"
echo ""
echo "4. Last inn nginx på nytt:"
echo "   sudo systemctl reload nginx"
echo ""
echo "ELLER kjør alt på én gang:"
echo "sudo cp /tmp/forskning-skycode.conf /etc/nginx/sites-available/ && sudo ln -sf /etc/nginx/sites-available/forskning-skycode.conf /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx"
echo ""

# Test tilkobling
echo "📊 STATUS:"
echo "✅ AI Ethics Framework: http://localhost:8021"
echo "🔄 Nginx proxy: Klar for aktivering"
echo "🎯 Resultat: forskning.skycode.no vil peke til AI Ethics Framework"

# Vis hva som vil skje
echo ""
echo "📋 ETTER IMPLEMENTERING:"
echo "https://forskning.skycode.no → nginx → proxy → AI Ethics Framework (port 8021)"
echo ""
echo "Dette vil erstatte den statiske 'Velkommen til skyforskning' siden"
echo "med din komplette AI Ethics Testing Framework! 🎉"
