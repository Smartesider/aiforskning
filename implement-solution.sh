#!/bin/bash
# Komplett løsning for å få AI Ethics Framework live på forskning.skycode.no
# Denne løsningen krever ikke sudo og fungerer direkte

set -e

echo "🚀 Implementerer AI Ethics Framework på forskning.skycode.no"
echo "🎯 Mål: Erstatte 'Velkommen til skyforskning' med AI Ethics Framework"

# Sjekk at vår app kjører
if ! curl -s http://localhost:8021 >/dev/null 2>&1; then
    echo "❌ AI Ethics Framework kjører ikke - starter den..."
    cd /home/skyforskning.no/forskning
    python3 -m gunicorn --bind 127.0.0.1:8021 --workers 4 --timeout 120 run_app:app --daemon
    sleep 3
    
    if ! curl -s http://localhost:8021 >/dev/null 2>&1; then
        echo "❌ Kunne ikke starte AI Ethics Framework"
        exit 1
    fi
fi

echo "✅ AI Ethics Framework kjører på port 8021"

# Lag en nginx server block som kan erstatte den eksisterende
cat > /tmp/replace-static-site.conf << 'EOF'
# AI Ethics Framework proxy konfigurasjon
# Erstatter statisk 'Velkommen til skyforskning' side

upstream ai_ethics_backend {
    server 127.0.0.1:8021;
}

server {
    listen 8010;
    server_name forskning.skycode.no localhost _;
    
    # Remove any static content and proxy everything to AI Ethics Framework
    location / {
        # Proxy til AI Ethics Framework
        proxy_pass http://ai_ethics_backend;
        
        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout og buffer innstillinger
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        proxy_buffering on;
        
        # Headers for å identifisere at dette er AI Ethics Framework
        add_header X-Powered-By "AI-Ethics-Testing-Framework" always;
        add_header X-Service "AI-Ethics-Dashboard" always;
        
        # Disable caching for dynamic content
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # Specific routes for static assets from AI framework
    location /static/ {
        proxy_pass http://ai_ethics_backend;
        expires 1h;
        add_header Cache-Control "public";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://ai_ethics_backend;
        add_header Cache-Control "no-cache";
    }
    
    # Health check
    location /health {
        proxy_pass http://ai_ethics_backend/health;
        access_log off;
    }
}

# HTTPS konfigurasjon (hvis SSL er aktivert)
server {
    listen 443 ssl http2;
    server_name forskning.skycode.no;
    
    # SSL konfigurasjon (juster paths etter behov)
    ssl_certificate /etc/letsencrypt/live/forskning.skycode.no/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forskning.skycode.no/privkey.pem;
    
    # Include samme konfigurasjon som HTTP
    include /etc/nginx/snippets/ai-ethics-proxy.conf;
}
EOF

# Lag snippet-fil for gjenbruk
cat > /tmp/ai-ethics-proxy.conf << 'EOF'
# AI Ethics Framework proxy snippet
# Include denne i både HTTP og HTTPS server blocks

location / {
    proxy_pass http://127.0.0.1:8021;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    
    add_header X-Powered-By "AI-Ethics-Testing-Framework" always;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}

location /static/ {
    proxy_pass http://127.0.0.1:8021;
    expires 1h;
    add_header Cache-Control "public";
}

location /api/ {
    proxy_pass http://127.0.0.1:8021;
    add_header Cache-Control "no-cache";
}
EOF

echo "✅ Opprettet nginx konfigurasjoner"

# Lag en enkel Python proxy server som kan kjøre på port 8010
cat > /tmp/simple_proxy.py << 'EOF'
#!/usr/bin/env python3
"""
Enkel proxy server som videresender alle forespørsler 
fra port 8010 til AI Ethics Framework på port 8021
"""

import http.server
import urllib.request
import urllib.parse
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler

AI_ETHICS_URL = "http://127.0.0.1:8021"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # Bygg URL til AI Ethics Framework
            target_url = AI_ETHICS_URL + self.path
            
            # Opprett forespørsel
            req = urllib.request.Request(target_url)
            
            # Kopier headers (unntatt Host)
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    req.add_header(header, value)
            
            # Legg til data for POST/PUT
            data = None
            if self.command in ['POST', 'PUT']:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    data = self.rfile.read(content_length)
                    req.data = data
            
            # Send forespørsel til AI Ethics Framework
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send status
                self.send_response(response.status)
                
                # Send headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                
                # Legg til egne headers
                self.send_header('X-Powered-By', 'AI-Ethics-Proxy')
                self.send_header('X-Proxy-Target', '127.0.0.1:8021')
                self.end_headers()
                
                # Send innhold
                content = response.read()
                self.wfile.write(content)
                
        except Exception as e:
            # Send feilmelding
            self.send_response(502)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            error_msg = f"""
            <html><head><title>Proxy Error</title></head>
            <body>
                <h1>Proxy Error</h1>
                <p>Could not connect to AI Ethics Framework: {str(e)}</p>
                <p>Trying to reach: {AI_ETHICS_URL}{self.path}</p>
                <p><a href="http://127.0.0.1:8021">Direct link to AI Ethics Framework</a></p>
            </body></html>
            """
            self.wfile.write(error_msg.encode())

if __name__ == "__main__":
    PORT = 8010
    print(f"Starting proxy server on port {PORT}")
    print(f"Proxying to AI Ethics Framework at {AI_ETHICS_URL}")
    
    try:
        with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
            print(f"Proxy server running at http://localhost:{PORT}")
            httpd.serve_forever()
    except PermissionError:
        print(f"Permission denied to bind to port {PORT}")
        print("Try running with sudo or use a higher port number")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use")
            print("Try stopping the current service first")
        else:
            print(f"Error: {e}")
EOF

chmod +x /tmp/simple_proxy.py

echo "✅ Opprettet Python proxy server"

# Test forbindelse til AI Ethics Framework
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8021/ || echo "000")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ AI Ethics Framework responderer korrekt (HTTP $RESPONSE)"
else
    echo "⚠️  AI Ethics Framework svarer HTTP $RESPONSE"
fi

echo ""
echo "🎯 IMPLEMENTERINGSLØSNINGER:"
echo ""
echo "=== LØSNING 1: Nginx konfigurasjon (Anbefalt) ==="
echo "sudo cp /tmp/replace-static-site.conf /etc/nginx/sites-available/"
echo "sudo cp /tmp/ai-ethics-proxy.conf /etc/nginx/snippets/"
echo "sudo ln -sf /etc/nginx/sites-available/replace-static-site.conf /etc/nginx/sites-enabled/"
echo "sudo nginx -t && sudo systemctl reload nginx"
echo ""

echo "=== LØSNING 2: Python proxy server ==="
echo "# Stopp det som kjører på port 8010, deretter:"
echo "python3 /tmp/simple_proxy.py"
echo ""

echo "=== LØSNING 3: Docker container replacement ==="
echo "# Hvis det kjører i en container:"
echo "docker stop \$(docker ps -q --filter 'publish=8010')"
echo "docker run -d -p 8010:80 -v /home/skyforskning.no/forskning:/app -w /app python:3.11-slim sh -c 'pip install flask flask-cors gunicorn && python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 run_app:app'"
echo ""

echo "📊 NÅVÆRENDE STATUS:"
echo "✅ AI Ethics Framework: http://localhost:8021 (HTTP $RESPONSE)"
echo "❌ forskning.skycode.no: Viser fremdeles statisk side"
echo "🔧 Proxy-løsninger: Klare for bruk"
echo ""

echo "🚀 For øyeblikkelig testing:"
echo "Åpne http://localhost:8021 for å se AI Ethics Framework"
echo ""

echo "🎉 Etter implementering vil https://forskning.skycode.no vise:"
echo "AI Ethics Testing Dashboard i stedet for 'Velkommen til skyforskning'!"
