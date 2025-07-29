#!/bin/bash

echo "🚀 Testing complete FastAPI + HTML5 + PWA deployment..."

# Check if FastAPI is running
echo "📊 Checking FastAPI status..."
if curl -s http://127.0.0.1:8010/api/health > /dev/null; then
    echo "✅ FastAPI backend is running on port 8010"
else
    echo "❌ FastAPI backend is not responding"
    exit 1
fi

# Test API endpoints
echo "🔍 Testing API endpoints..."

echo "  Testing health endpoint..."
HEALTH=$(curl -s http://127.0.0.1:8010/api/health | jq -r '.status' 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
    echo "  ✅ Health endpoint OK"
else
    echo "  ❌ Health endpoint failed"
fi

echo "  Testing models endpoint..."
MODELS=$(curl -s http://127.0.0.1:8010/api/available-models | jq -r '.total' 2>/dev/null)
if [ "$MODELS" -gt 0 ]; then
    echo "  ✅ Models endpoint OK ($MODELS models available)"
else
    echo "  ❌ Models endpoint failed"
fi

# Check static files
echo "📁 Checking static files..."
if [ -f "/home/skyforskning.no/public_html/index.html" ]; then
    echo "✅ Frontend files exist"
else
    echo "❌ Frontend files missing"
fi

# Show running processes
echo "🔄 Running processes:"
ps aux | grep -E "(python.*main.py|nginx)" | grep -v grep

echo ""
echo "🎯 Deployment Summary:"
echo "   Backend: FastAPI running on http://127.0.0.1:8010"
echo "   Frontend: HTML5 + PWA at /home/skyforskning.no/public_html"
echo "   API Docs: http://127.0.0.1:8010/api/docs"
echo "   Health: http://127.0.0.1:8010/api/health"
echo ""
echo "🔗 Next Steps:"
echo "   1. Configure nginx with: nginx-fastapi.conf"
echo "   2. Set up systemd service for production"
echo "   3. Configure SSL certificate"
echo "   4. Test PWA functionality"
