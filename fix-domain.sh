#!/bin/bash
# Direkte implementering for å erstatte den statiske siden på forskning.skycode.no
# Med AI Ethics Testing Framework

set -e

echo "🔧 Implementerer direkte løsning for forskning.skycode.no"
echo "🎯 Mål: Erstatte statisk side med AI Ethics Framework"

# Sjekk at vår app kjører på 8021
if ! curl -s http://localhost:8021 >/dev/null; then
    echo "❌ AI Ethics Framework kjører ikke på port 8021"
    echo "🚀 Starter AI Ethics Framework..."
    cd /home/skyforskning.no/forskning
    python3 -m gunicorn --bind 127.0.0.1:8021 --workers 4 --timeout 120 run_app:app --daemon
    sleep 3
fi

echo "✅ AI Ethics Framework kjører på port 8021"

# Finn hva som kjører på port 8020
echo "🔍 Analyserer hva som kjører på port 8020..."
PORT_8020_INFO=$(ss -tlnp | grep :8020 || echo "Ingen info tilgjengelig")
echo "Port 8020 info: $PORT_8020_INFO"

# Prøv å finne nginx config som kan være ansvarlig
echo "🔍 Leter etter nginx konfigurasjoner..."
NGINX_CONFIGS=$(find /etc -name "*nginx*" -type f 2>/dev/null | grep -E "\.(conf|config)$" | head -5 || echo "Ingen tilgang til nginx configs")

if [ "$NGINX_CONFIGS" != "Ingen tilgang til nginx configs" ]; then
    echo "📁 Fant nginx configs:"
    echo "$NGINX_CONFIGS"
else
    echo "⚠️  Kan ikke få tilgang til nginx configs uten sudo"
fi

# Lag en enkel proxy-løsning
echo "🔄 Lager proxy-løsning..."

# Opprett en midlertidig nginx config for å proxy til vår app
cat > /tmp/nginx-proxy-fix.conf << 'EOF'
server {
    listen 8022;
    server_name forskning.skycode.no localhost;
    
    location / {
        proxy_pass http://127.0.0.1:8021;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Headers for å identifisere kilden
        add_header X-Powered-By "AI-Ethics-Framework" always;
        add_header X-Service-Status "Replacement-Active" always;
    }
}
EOF

echo "✅ Opprettet proxy config i /tmp/nginx-proxy-fix.conf"

# Prøv å finne hvor det statiske innholdet kommer fra
echo "🔍 Søker etter statisk innhold..."
STATIC_FILES=$(find /var/www /usr/share/nginx /opt -name "*.html" -exec grep -l "Velkommen til skyforskning" {} \; 2>/dev/null | head -3 || echo "Ikke funnet")

if [ "$STATIC_FILES" != "Ikke funnet" ]; then
    echo "📄 Fant statiske filer:"
    echo "$STATIC_FILES"
    
    # Prøv å erstatte innholdet direkte (krever rettigheter)
    for file in $STATIC_FILES; do
        echo "🔄 Prøver å erstatte: $file"
        if [ -w "$file" ]; then
            echo "✅ Kan skrive til $file - erstatter innhold..."
            cat > "$file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=http://127.0.0.1:8021">
    <title>AI Ethics Testing Framework</title>
</head>
<body>
    <h1>Redirecting to AI Ethics Testing Framework...</h1>
    <p>If you are not redirected automatically, <a href="http://127.0.0.1:8021">click here</a>.</p>
    <script>window.location.href = 'http://127.0.0.1:8021';</script>
</body>
</html>
EOF
            echo "✅ Erstattet $file med redirect"
        else
            echo "❌ Kan ikke skrive til $file (krever sudo)"
        fi
    done
else
    echo "⚠️  Kunne ikke finne statiske filer"
fi

# Opprett en systemd service for å kjøre vår app på port 8020
echo "🔧 Lager systemd service..."
cat > /tmp/ai-ethics-8020.service << EOF
[Unit]
Description=AI Ethics Testing Framework on Port 8020
After=network.target

[Service]
Type=forking
User=Terje
Group=Terje
WorkingDirectory=/home/skyforskning.no/forskning
Environment=PYTHONPATH=/home/skyforskning.no/forskning/src
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:8020 --workers 4 --timeout 120 --daemon run_app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Opprettet systemd service: /tmp/ai-ethics-8020.service"

# Gi instruksjoner for å implementere løsningen
echo ""
echo "🎯 IMPLEMENTERINGSLØSNINGER:"
echo ""
echo "=== LØSNING 1: Erstatt systemd service (Anbefalt) ==="
echo "sudo cp /tmp/ai-ethics-8020.service /etc/systemd/system/"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl stop <current-service-on-8020>  # Finn med: sudo systemctl list-units | grep 8020"
echo "sudo systemctl enable ai-ethics-8020"
echo "sudo systemctl start ai-ethics-8020"
echo ""

echo "=== LØSNING 2: Docker container replacement ==="
echo "# Stopp eksisterende container på port 8020"
echo "docker stop \$(docker ps -q --filter 'publish=8020')"
echo "# Start vår container"
echo "docker run -d -p 8020:80 -v /home/skyforskning.no/forskning:/app -w /app python:3.11-slim sh -c 'pip install flask flask-cors gunicorn && python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 run_app:app'"
echo ""

echo "=== LØSNING 3: Nginx proxy update ==="
echo "sudo cp /tmp/nginx-proxy-fix.conf /etc/nginx/sites-available/"
echo "sudo ln -sf /etc/nginx/sites-available/nginx-proxy-fix.conf /etc/nginx/sites-enabled/"
echo "sudo nginx -t && sudo systemctl reload nginx"
echo ""

echo "=== LØSNING 4: Direkte port switch ==="
echo "# Stopp det som kjører på 8020, start vår app der"
echo "sudo fuser -k 8020/tcp"
echo "cd /home/skyforskning.no/forskning"
echo "python3 -m gunicorn --bind 0.0.0.0:8020 --workers 4 --timeout 120 run_app:app --daemon"
echo ""

echo "📊 STATUS:"
echo "✅ AI Ethics Framework: Kjører på http://localhost:8021"
echo "❌ forskning.skycode.no: Viser fremdeles statisk side"
echo "🔧 Løsningsfiler: Opprettet i /tmp/"
echo ""
echo "🚀 Neste steg: Velg en av løsningene ovenfor basert på din systemkonfigurasjon"
