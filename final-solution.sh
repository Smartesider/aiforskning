#!/bin/bash
# Endelig løsning: Erstatt statisk innhold på forskning.skycode.no
# med AI Ethics Testing Framework

set -e

echo "🎯 ENDELIG LØSNING: forskning.skycode.no → AI Ethics Framework"

# Stopp eksisterende proxy forsøk
pkill -f "simple_proxy.py" 2>/dev/null || true

# Stopp eksisterende gunicorn instanser for denne appen
pkill -f "run_app:app" 2>/dev/null || true

echo "🔄 Starter AI Ethics Framework med optimerte innstillinger..."

# Start AI Ethics Framework med det oppdaterte skriptet
cd /home/skyforskning.no/forskning
./start_server.sh &

# Vent litt og sjekk status
sleep 5

# Sjekk hvilken port den kjører på
if curl -s http://localhost:8020 | grep -q "AI Ethics\|DOCTYPE"; then
    echo "🎉 SUKSESS! AI Ethics Framework kjører på port 8020"
    echo "✅ https://forskning.skycode.no skal nå vise AI Ethics Framework"
    
    # Test respons
    TITLE=$(curl -s http://localhost:8020 | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g' || echo "Ingen tittel funnet")
    echo "📄 Sidetittel: $TITLE"
    
elif curl -s http://localhost:8022 | grep -q "AI Ethics\|DOCTYPE"; then
    echo "🔧 AI Ethics Framework kjører på port 8022"
    echo "⚠️  Trenger nginx proxy for å koble til forskning.skycode.no"
    echo ""
    echo "🚀 Kjør denne kommandoen for å fullføre:"
    echo "sudo cp /tmp/replace-static-site.conf /etc/nginx/sites-available/ && sudo cp /tmp/ai-ethics-proxy.conf /etc/nginx/snippets/ && sudo ln -sf /etc/nginx/sites-available/replace-static-site.conf /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx"
    
else
    echo "❌ Kunne ikke starte AI Ethics Framework"
    echo "🔍 Prøver diagnostikk..."
    
    # Vis prosess status
    ps aux | grep -E "(gunicorn|run_app)" | grep -v grep
    
    # Vis tilgjengelige porter
    echo "📊 Port status:"
    for port in 8020 8021 8022; do
        if curl -s http://localhost:$port >/dev/null 2>&1; then
            echo "  Port $port: ✅ Aktiv"
        else
            echo "  Port $port: ❌ Inaktiv"
        fi
    done
fi

# Gi status oppdatering
echo ""
echo "📊 NÅVÆRENDE STATUS:"
echo "🌐 Test lokal tilgang:"
echo "  - Port 8020: http://localhost:8020"
echo "  - Port 8021: http://localhost:8021" 
echo "  - Port 8022: http://localhost:8022"
echo ""
echo "🎯 Mål: https://forskning.skycode.no → AI Ethics Testing Dashboard"
echo ""

# Vis prosesser som kjører
PROCESSES=$(ps aux | grep -E "(gunicorn.*run_app|python.*start_server)" | grep -v grep | wc -l)
echo "🔄 AI Ethics prosesser kjører: $PROCESSES"

if [ "$PROCESSES" -gt 0 ]; then
    echo "✅ AI Ethics Framework er i drift!"
    echo ""
    echo "🚀 For å teste direkte:"
    echo "Åpne en av disse URL-ene i nettleseren:"
    echo "  - http://localhost:8020 (hvis tilgjengelig)"
    echo "  - http://localhost:8021"
    echo "  - http://localhost:8022"
    echo ""
    echo "🎉 Du skal se 'AI Ethics Testing Dashboard' i stedet for 'Velkommen til skyforskning'!"
fi
