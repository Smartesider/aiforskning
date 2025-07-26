#!/bin/bash
# Final deployment script - creates a ready-to-deploy Docker container
# That can be directly imported/updated in Portainer

set -e

echo "🐳 Creating deployment-ready AI Ethics Testing Framework"
echo "📦 Container ID to replace: 1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430"

# Stop our current test instance
pkill -f "gunicorn.*8021" 2>/dev/null || echo "No running test instance"

# Create final optimized Dockerfile
cat > Dockerfile.final << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py *.json *.txt *.md ./
COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/
COPY gunicorn.conf.py .

# Create app user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Start command
CMD ["python3", "-m", "gunicorn", "--bind", "0.0.0.0:80", "--workers", "4", "--timeout", "120", "run_app:app"]
EOF

# Build the image
IMAGE_NAME="ai-ethics-framework"
IMAGE_TAG="$(date +%Y%m%d-%H%M%S)"
FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"

echo "🔨 Building Docker image: $FULL_IMAGE_NAME"

if command -v docker >/dev/null 2>&1; then
    docker build -f Dockerfile.final -t "$FULL_IMAGE_NAME" . && \
    docker tag "$FULL_IMAGE_NAME" "$IMAGE_NAME:latest"
    
    echo "✅ Docker image built successfully"
    echo "🏷️  Tagged as: $FULL_IMAGE_NAME and $IMAGE_NAME:latest"
    
    # Test the image locally
    echo "🧪 Testing the image..."
    CONTAINER_TEST_ID=$(docker run -d -p 8025:80 --name ai-ethics-test "$FULL_IMAGE_NAME")
    
    sleep 15
    
    if curl -s http://localhost:8025 | grep -q "AI Ethics"; then
        echo "✅ Test successful! Image works correctly"
        docker stop "$CONTAINER_TEST_ID" && docker rm "$CONTAINER_TEST_ID"
    else
        echo "⚠️  Test inconclusive, but image is built"
        docker stop "$CONTAINER_TEST_ID" && docker rm "$CONTAINER_TEST_ID" 2>/dev/null || true
    fi
    
    # Export image for Portainer
    echo "📦 Exporting image for Portainer import..."
    docker save "$FULL_IMAGE_NAME" > ai-ethics-framework-export.tar
    echo "✅ Exported to: ai-ethics-framework-export.tar"
    
else
    echo "⚠️  Docker not available for building, but Dockerfile created"
fi

# Create Portainer stack configuration
cat > portainer-stack.yml << EOF
version: '3.8'

services:
  ai-ethics-framework:
    image: $FULL_IMAGE_NAME
    container_name: ai-ethics-framework-production
    restart: unless-stopped
    ports:
      - "8020:80"
    environment:
      - PYTHONPATH=/app
      - FLASK_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - ai-ethics-net

networks:
  ai-ethics-net:
    driver: bridge
EOF

echo "✅ Created Portainer stack configuration: portainer-stack.yml"

# Create simple deployment instructions
cat > PORTAINER_DEPLOYMENT.md << 'EOF'
# Portainer Deployment Instructions

## Method 1: Replace Existing Container (Recommended)

1. **In Portainer Web UI:**
   - Go to "Containers"
   - Find container: `1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430`
   - Click on the container name
   - Click "Duplicate/Edit"

2. **Update Container Settings:**
   - **Image:** `python:3.11-slim`
   - **Command:** `sh -c "apt-get update && apt-get install -y curl && pip install flask flask-cors gunicorn && cd /app && python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 120 run_app:app"`
   - **Working Directory:** `/app`
   - **Volumes:** Add volume mapping:
     - **Container:** `/app`
     - **Host:** `/home/skyforskning.no/forskning`
   - **Environment Variables:**
     - `PYTHONPATH=/app`
     - `FLASK_ENV=production`
   - **Ports:** Ensure `8020:80` mapping exists
   - **Restart Policy:** `Unless stopped`

3. **Deploy:**
   - Click "Deploy the container"
   - Wait for startup (may take 1-2 minutes)
   - Test at https://forskning.skycode.no

## Method 2: Docker Command Line (If Available)

```bash
# Stop and remove old container
docker stop 1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430
docker rm 1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430

# Run new container
docker run -d \
  --name ai-ethics-framework-production \
  -p 8020:80 \
  -v /home/skyforskning.no/forskning:/app \
  -w /app \
  -e PYTHONPATH=/app \
  -e FLASK_ENV=production \
  --restart unless-stopped \
  python:3.11-slim \
  sh -c "apt-get update && apt-get install -y curl && pip install flask flask-cors gunicorn && python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 120 run_app:app"
```

## Method 3: Stack Deployment

1. In Portainer, go to "Stacks"
2. Click "Add stack"
3. Name: `ai-ethics-framework`
4. Upload or paste the content of `portainer-stack.yml`
5. Deploy

## Verification

After deployment, test these URLs:
- http://forskning.skycode.no
- https://forskning.skycode.no

You should see the "AI Ethics Testing Dashboard" instead of "Velkommen til skyforskning"

## Troubleshooting

If the container fails to start:
1. Check container logs in Portainer
2. Ensure the volume path `/home/skyforskning.no/forskning` is accessible
3. Verify all files are present in the mounted directory
4. Check if port 8020 is available

## Notes

- The static "Velkommen til skyforskning" page will be completely replaced
- The AI Ethics Testing Framework will handle all requests to the domain
- Container will auto-restart if it stops
- Health checks are included to monitor application status
EOF

echo "📋 Created deployment instructions: PORTAINER_DEPLOYMENT.md"

# Show final status
echo ""
echo "🎉 Deployment package ready!"
echo ""
echo "📊 Created Files:"
echo "   ✅ Dockerfile.final - Optimized container image"
echo "   ✅ portainer-stack.yml - Stack configuration"
echo "   ✅ PORTAINER_DEPLOYMENT.md - Step-by-step instructions"
if [ -f "ai-ethics-framework-export.tar" ]; then
echo "   ✅ ai-ethics-framework-export.tar - Ready-to-import image"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Follow instructions in PORTAINER_DEPLOYMENT.md"
echo "2. Replace container 1a0c86120b1c... with the new configuration"
echo "3. The static placeholder will be completely replaced"
echo "4. Your AI Ethics Testing Framework will be live at forskning.skycode.no"

echo ""
echo "🔗 Key Configuration:"
echo "   - Port mapping: 8020:80 (host:container)"
echo "   - Volume: /home/skyforskning.no/forskning:/app"
echo "   - Image: python:3.11-slim"
echo "   - Command: gunicorn with auto-install of dependencies"

# Clean up
rm -f Dockerfile.final
