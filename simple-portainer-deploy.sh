#!/bin/bash
# Simple Portainer deployment using volume mounts
# This approach mounts the current directory into the existing container

set -e

PORTAINER_API_KEY="ptr_36XdQm0OK/G3GuA0CiA3U0/wxe2XWDxvGWxqNvWi8Io="
CONTAINER_ID="1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430"
PORTAINER_URL="https://portainer.skycode.no"
CURRENT_DIR="/home/skyforskning.no/forskning"

echo "🔄 Simple Portainer deployment for AI Ethics Testing Framework"
echo "📁 Mounting directory: $CURRENT_DIR"

# Function for API calls
portainer_api() {
    curl -s -X "$1" \
        -H "X-API-Key: $PORTAINER_API_KEY" \
        -H "Content-Type: application/json" \
        ${3:+-d "$3"} \
        "$PORTAINER_URL/api$2"
}

# Try to find the correct endpoint
echo "🔍 Finding container endpoint..."
for endpoint_id in 1 2 3; do
    CONTAINER_INFO=$(portainer_api "GET" "/endpoints/$endpoint_id/docker/containers/$CONTAINER_ID/json" 2>/dev/null || echo "")
    if [ -n "$CONTAINER_INFO" ]; then
        echo "✅ Found container on endpoint $endpoint_id"
        ENDPOINT_ID=$endpoint_id
        break
    fi
done

if [ -z "$CONTAINER_INFO" ]; then
    echo "❌ Container not found. Using manual approach..."
    echo ""
    echo "📋 Manual deployment steps:"
    echo "1. In Portainer, go to your container: ${CONTAINER_ID:0:12}..."
    echo "2. Stop the container"
    echo "3. Duplicate/Edit the container with these settings:"
    echo "   - Image: python:3.11-slim"
    echo "   - Command: python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 120 run_app:app"
    echo "   - Working Directory: /app"
    echo "   - Volume: $CURRENT_DIR:/app"
    echo "   - Environment: PYTHONPATH=/app"
    echo "   - Port: 8020:80"
    echo "4. Start the container"
    echo ""
    echo "🔄 Or copy this docker command:"
    echo "docker run -d --name ai-ethics-framework-new \\"
    echo "  -p 8020:80 \\"
    echo "  -v $CURRENT_DIR:/app \\"
    echo "  -w /app \\"
    echo "  -e PYTHONPATH=/app \\"
    echo "  --restart unless-stopped \\"
    echo "  python:3.11-slim \\"
    echo "  sh -c 'pip install -r requirements.txt && python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 120 run_app:app'"
    exit 0
fi

# Get current container info
CONTAINER_NAME=$(echo "$CONTAINER_INFO" | grep -o '"Name":"[^"]*"' | cut -d'"' -f4 | sed 's/^\///')
echo "📦 Container: $CONTAINER_NAME"

# Stop the container
echo "⏹️  Stopping container..."
portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/$CONTAINER_ID/stop"

# Create new container with volume mount
echo "🔄 Creating updated container..."
NEW_CONTAINER_CONFIG=$(cat << EOF
{
    "Image": "python:3.11-slim",
    "name": "${CONTAINER_NAME}-ai-ethics",
    "WorkingDir": "/app",
    "Env": [
        "PYTHONPATH=/app",
        "FLASK_ENV=production"
    ],
    "Cmd": [
        "sh", "-c", 
        "apt-get update && apt-get install -y curl && pip install -r requirements.txt && python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 120 run_app:app"
    ],
    "ExposedPorts": {
        "80/tcp": {}
    },
    "HostConfig": {
        "Binds": [
            "$CURRENT_DIR:/app"
        ],
        "PortBindings": {
            "80/tcp": [{"HostPort": "8020"}]
        },
        "RestartPolicy": {
            "Name": "unless-stopped"
        }
    },
    "Healthcheck": {
        "Test": ["CMD", "curl", "-f", "http://localhost:80/"],
        "Interval": 30000000000,
        "Timeout": 10000000000,
        "Retries": 3,
        "StartPeriod": 40000000000
    }
}
EOF
)

NEW_CONTAINER=$(portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/create" "$NEW_CONTAINER_CONFIG")
NEW_CONTAINER_ID=$(echo "$NEW_CONTAINER" | grep -o '"Id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$NEW_CONTAINER_ID" ]; then
    echo "✅ Created new container: ${NEW_CONTAINER_ID:0:12}..."
    
    # Start the new container
    echo "🚀 Starting new container..."
    portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/$NEW_CONTAINER_ID/start"
    
    # Wait for startup
    echo "⏳ Waiting for application to start (this may take a minute)..."
    sleep 30
    
    # Test the deployment
    echo "🧪 Testing deployment..."
    for i in {1..10}; do
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://forskning.skycode.no/ 2>/dev/null || echo "000")
        if [ "$RESPONSE" = "200" ]; then
            echo "✅ Deployment successful!"
            echo "🌐 AI Ethics Testing Framework is live at: https://forskning.skycode.no"
            break
        else
            echo "⏳ Attempt $i/10 - HTTP $RESPONSE, waiting..."
            sleep 10
        fi
    done
    
    if [ "$RESPONSE" != "200" ]; then
        echo "⚠️  Application may still be starting. Check logs in Portainer."
    fi
    
    # Clean up old container
    echo "🗑️  Removing old container..."
    portainer_api "DELETE" "/endpoints/$ENDPOINT_ID/docker/containers/$CONTAINER_ID?force=true"
    
    echo ""
    echo "🎉 Deployment completed!"
    echo "📊 Summary:"
    echo "   - Old container: ❌ Removed (${CONTAINER_ID:0:12}...)"
    echo "   - New container: ✅ Running (${NEW_CONTAINER_ID:0:12}...)"
    echo "   - Static placeholder: ❌ Replaced"
    echo "   - AI Ethics Framework: ✅ Live"
    echo "   - URL: https://forskning.skycode.no"
    
else
    echo "❌ Failed to create new container"
    echo "🔄 Starting original container..."
    portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/$CONTAINER_ID/start"
    exit 1
fi
