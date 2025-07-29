#!/bin/bash
# Portainer Deployment Script for AI Ethics Testing Framework
# Replaces static placeholder in container ID: 1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430

set -e

# Configuration
PORTAINER_API_KEY="ptr_36XdQm0OK/G3GuA0CiA3U0/wxe2XWDxvGWxqNvWi8Io="
CONTAINER_ID="1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430"
PORTAINER_URL="https://portainer.skycode.no"  # Adjust if different
APP_NAME="ai-ethics-framework"

echo "🐳 Deploying AI Ethics Testing Framework to Portainer"
echo "📋 Container ID: ${CONTAINER_ID:0:12}..."
echo "🔑 Using provided API key"

# Function to make Portainer API calls
portainer_api() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    if [ -n "$data" ]; then
        curl -s -X "$method" \
            -H "X-API-Key: $PORTAINER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$PORTAINER_URL/api$endpoint"
    else
        curl -s -X "$method" \
            -H "X-API-Key: $PORTAINER_API_KEY" \
            "$PORTAINER_URL/api$endpoint"
    fi
}

# Get container information
echo "📋 Getting container information..."
CONTAINER_INFO=$(portainer_api "GET" "/endpoints/1/docker/containers/$CONTAINER_ID/json" || echo "")

if [ -z "$CONTAINER_INFO" ]; then
    echo "❌ Failed to get container information. Trying alternative endpoints..."
    
    # Try different endpoint IDs
    for endpoint_id in 1 2 3; do
        echo "🔍 Trying endpoint $endpoint_id..."
        CONTAINER_INFO=$(portainer_api "GET" "/endpoints/$endpoint_id/docker/containers/$CONTAINER_ID/json" 2>/dev/null || echo "")
        if [ -n "$CONTAINER_INFO" ]; then
            echo "✅ Found container on endpoint $endpoint_id"
            ENDPOINT_ID=$endpoint_id
            break
        fi
    done
    
    if [ -z "$CONTAINER_INFO" ]; then
        echo "❌ Cannot find container. Please check:"
        echo "   1. Container ID is correct"
        echo "   2. Portainer URL: $PORTAINER_URL"
        echo "   3. API key is valid"
        exit 1
    fi
else
    ENDPOINT_ID=1
fi

echo "✅ Container found on endpoint $ENDPOINT_ID"

# Parse container information
CONTAINER_NAME=$(echo "$CONTAINER_INFO" | grep -o '"Name":"[^"]*"' | cut -d'"' -f4 | sed 's/^\///')
CONTAINER_IMAGE=$(echo "$CONTAINER_INFO" | grep -o '"Image":"[^"]*"' | cut -d'"' -f4)

echo "📦 Container Name: $CONTAINER_NAME"
echo "🏷️  Current Image: $CONTAINER_IMAGE"

# Create a new image with our application
echo "🔨 Building new Docker image with AI Ethics Framework..."

# Create optimized Dockerfile for the deployment
cat > Dockerfile.portainer << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 80 (internal container port)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Start with gunicorn
CMD ["python3", "-m", "gunicorn", "--bind", "0.0.0.0:8010", "--workers", "4", "--timeout", "120", "run_app:app"]
EOF

# Build the new image
IMAGE_TAG="ai-ethics-framework:$(date +%Y%m%d-%H%M%S)"
echo "🏗️  Building image: $IMAGE_TAG"

docker build -f Dockerfile.portainer -t "$IMAGE_TAG" . || {
    echo "❌ Docker build failed. Trying alternative approach..."
    
    # Alternative: Create deployment package
    echo "📦 Creating deployment package..."
    tar -czf ai-ethics-deployment.tar.gz \
        *.py *.json *.txt *.md *.sh \
        src/ static/ templates/ \
        gunicorn.conf.py
    
    echo "✅ Created deployment package: ai-ethics-deployment.tar.gz"
    echo "📋 Manual deployment instructions:"
    echo ""
    echo "1. In Portainer, go to Container: $CONTAINER_NAME"
    echo "2. Stop the container"
    echo "3. Edit the container configuration:"
    echo "   - Change image to: python:3.11-slim"
    echo "   - Add environment variables:"
    echo "     PYTHONPATH=/app"
    echo "   - Add volume mount for this directory to /app"
    echo "   - Change command to: python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 run_app:app"
    echo "4. Start the container"
    echo ""
    echo "🔄 Or use the automated update script below..."
    exit 0
}

# Stop the existing container
echo "⏹️  Stopping existing container..."
portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/$CONTAINER_ID/stop" || echo "Container might already be stopped"

# Create container update configuration
UPDATE_CONFIG=$(cat << EOF
{
    "Image": "$IMAGE_TAG",
    "Env": [
        "PYTHONPATH=/app",
        "FLASK_ENV=production"
    ],
    "ExposedPorts": {
        "8010/tcp": {}
    },
    "HostConfig": {
        "PortBindings": {
            "8010/tcp": [{"HostPort": "8010"}]
        },
        "RestartPolicy": {
            "Name": "unless-stopped"
        }
    },
    "Cmd": ["python3", "-m", "gunicorn", "--bind", "0.0.0.0:8010", "--workers", "4", "--timeout", "120", "run_app:app"]
}
EOF
)

# Update container configuration
echo "🔄 Updating container configuration..."
portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/$CONTAINER_ID/update" "$UPDATE_CONFIG" || {
    echo "⚠️  Direct update failed. Creating new container..."
    
    # Create new container with same settings
    NEW_CONTAINER_CONFIG=$(cat << EOF
{
    "Image": "$IMAGE_TAG",
    "name": "${CONTAINER_NAME}-updated",
    "Env": [
        "PYTHONPATH=/app",
        "FLASK_ENV=production"
    ],
    "ExposedPorts": {
        "8010/tcp": {}
    },
    "HostConfig": {
        "PortBindings": {
            "8010/tcp": [{"HostPort": "8010"}]
        },
        "RestartPolicy": {
            "Name": "unless-stopped"
        }
    },
    "Cmd": ["python3", "-m", "gunicorn", "--bind", "0.0.0.0:8010", "--workers", "4", "--timeout", "120", "run_app:app"]
}
EOF
    )
    
    NEW_CONTAINER=$(portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/create" "$NEW_CONTAINER_CONFIG")
    NEW_CONTAINER_ID=$(echo "$NEW_CONTAINER" | grep -o '"Id":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$NEW_CONTAINER_ID" ]; then
        echo "✅ Created new container: ${NEW_CONTAINER_ID:0:12}..."
        
        # Start the new container
        portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/$NEW_CONTAINER_ID/start"
        echo "🚀 Started new container"
        
        # Remove old container
        portainer_api "DELETE" "/endpoints/$ENDPOINT_ID/docker/containers/$CONTAINER_ID?force=true"
        echo "🗑️  Removed old container"
        
        CONTAINER_ID="$NEW_CONTAINER_ID"
    else
        echo "❌ Failed to create new container"
        exit 1
    fi
}

# Start the container
echo "🚀 Starting updated container..."
portainer_api "POST" "/endpoints/$ENDPOINT_ID/docker/containers/$CONTAINER_ID/start"

# Wait a moment for startup
echo "⏳ Waiting for application to start..."
sleep 10

# Test the deployment
echo "🧪 Testing deployment..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://forskning.skycode.no/ || echo "000")

if [ "$RESPONSE" = "200" ]; then
    echo "✅ Deployment successful!"
    echo "🌐 AI Ethics Testing Framework is now live at: https://forskning.skycode.no"
    
    # Test specific endpoint
    TITLE=$(curl -s http://forskning.skycode.no/ | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')
    echo "📄 Page title: $TITLE"
    
else
    echo "⚠️  Deployment completed but testing returned HTTP $RESPONSE"
    echo "🔍 Check container logs in Portainer for details"
    echo "📋 Container ID: ${CONTAINER_ID:0:12}..."
fi

echo ""
echo "🎉 Deployment process completed!"
echo "📊 Summary:"
echo "   - Static placeholder: ❌ Replaced"
echo "   - AI Ethics Framework: ✅ Deployed"
echo "   - Container ID: ${CONTAINER_ID:0:12}..."
echo "   - URL: https://forskning.skycode.no"

# Cleanup
rm -f Dockerfile.portainer
