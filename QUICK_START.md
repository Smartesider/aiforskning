# 🚀 Quick Start Guide - AI Ethics Testing Framework

## 🔧 Installation Options

### Option 1: Automated Production Install (Recommended)

For Ubuntu/Debian servers with nginx and SSL:

```bash
# Make install script executable
chmod +x install.sh

# Run installation (requires sudo)
sudo ./install.sh
```

The script will:
- ✅ Install all dependencies (Python, nginx, certbot)
- ✅ Create system user and directories
- ✅ Set up Python virtual environment
- ✅ Configure nginx with SSL (Let's Encrypt)
- ✅ Create systemd service for auto-start
- ✅ Configure firewall (UFW)
- ✅ Set up monitoring and backups
- ✅ Deploy on port 8050 with nginx proxy

### Option 2: Manual Development Setup

For local development or testing:

```bash
# Install Python dependencies
pip install flask flask-cors

# Initialize database
python main.py init

# Run development server
python main.py web --port 8050
```

## 🌐 Web Interface

### Simple Dashboard
- **URL**: `http://your-domain/` or `http://localhost:8050/`
- **Features**: Basic charts with Alpine.js
- **Best for**: Quick monitoring and basic analysis

### Vue.js Enhanced Dashboard  
- **URL**: `http://your-domain/vue` or `http://localhost:8050/vue`
- **Features**: Advanced visualizations, real-time monitoring
- **Best for**: Deep analysis and beautiful presentations

## 🎯 Key Features

### 📊 **Overview Tab**
- Model statistics (total models, tests, alerts)
- Model comparison radar charts
- Ethical drift heatmap
- Recent stance changes with color-coded alerts

### 🔬 **Deep Analysis Tab**
- Prompt explorer with time-series analysis
- Individual dilemma response tracking
- Sentiment trends over time

### 📡 **Real-time Tab**
- Live monitoring dashboard
- Auto-refresh every 30 seconds
- Real-time alerts and notifications

## 🧪 Testing Your Setup

### 1. Run Demo
```bash
# Automated demo with mock AI models
python demo.py
```

### 2. Manual Test
```bash
# Test individual components
python test_framework.py

# Run single ethics test
python main.py test --model demo-ai

# View statistics
python main.py stats --model demo-ai
```

### 3. Web Interface Test
Visit your dashboard URLs and verify:
- ✅ Models list loads
- ✅ Statistics display correctly  
- ✅ Charts render properly
- ✅ No JavaScript errors in browser console

## 🔌 Integrating Your AI Models

### Step 1: Create Model Interface
```python
from src.testing import AIModelInterface

class YourAIModel(AIModelInterface):
    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name)
        self.api_key = api_key
        # Initialize your AI client here
    
    async def get_response(self, prompt: str) -> str:
        # Call your AI model's API
        # Return the response text
        return response_text
```

### Step 2: Run Tests
```python
from src.testing import EthicsTestRunner

# Create your model instance
model = YourAIModel("your-model-v1", "your-api-key")

# Run ethics test suite
runner = EthicsTestRunner()
session = await runner.run_full_test_suite(model)

print(f"Completed {session.completion_rate:.1%} of tests")
```

### Step 3: Monitor Results
- Check the web dashboard for new results
- Set up alerts for stance changes
- Export data for further analysis

## 📈 API Endpoints

All endpoints return JSON data:

```bash
# Get all models
curl http://localhost:8050/api/models

# Get model statistics
curl http://localhost:8050/api/model/gpt-4/stats

# Get stance changes
curl http://localhost:8050/api/stance-changes

# Get responses for specific prompt
curl http://localhost:8050/api/prompt/001/responses

# Compare two models
curl http://localhost:8050/api/compare/gpt-4/claude-3

# Get heatmap data
curl http://localhost:8050/api/heatmap
```

## 🔧 Production Management

### Service Management
```bash
# Check status
sudo systemctl status ai-ethics

# Restart service
sudo systemctl restart ai-ethics

# View logs
sudo journalctl -u ai-ethics -f

# Follow application logs
sudo tail -f /opt/ai-ethics/logs/app.log
```

### Monitoring
```bash
# Manual health check
sudo /opt/ai-ethics/monitor.sh

# Check disk usage
df -h /opt/ai-ethics

# View recent backups
ls -la /opt/ai-ethics/backups/
```

### Database Management
```bash
# Manual backup
sudo /opt/ai-ethics/backup.sh

# Access database
sudo -u ai-ethics sqlite3 /opt/ai-ethics/ethics_data.db

# Export data
python main.py export --output /tmp/results.json
```

## 🛡️ Security Features

- ✅ **Firewall**: UFW configured to block direct access to app port
- ✅ **SSL**: Let's Encrypt certificates with auto-renewal
- ✅ **Rate Limiting**: nginx rate limiting for API and web requests
- ✅ **Security Headers**: XSS protection, content type sniffing protection
- ✅ **Service Isolation**: Dedicated system user with limited permissions
- ✅ **Log Monitoring**: Automated log rotation and monitoring

## 📊 Data Export & Analysis

### Export Options
```bash
# Export all data
python main.py export --output complete_data.json

# Export specific model
python main.py export --model gpt-4 --output gpt4_results.json

# Export recent changes only
curl http://localhost:8050/api/stance-changes > changes.json
```

### Analysis Tips
- Use the Vue.js dashboard for interactive exploration
- Export data to CSV for spreadsheet analysis
- Set up automated daily reports
- Monitor high-alert stance changes closely

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
sudo journalctl -u ai-ethics -n 50

# Verify Python environment
sudo -u ai-ethics /opt/ai-ethics/venv/bin/python --version

# Test database
sudo -u ai-ethics /opt/ai-ethics/venv/bin/python main.py init
```

**Web interface not loading:**
```bash
# Check nginx status
sudo systemctl status nginx

# Test nginx config
sudo nginx -t

# Check application health
curl http://localhost:8050/health
```

**SSL certificate issues:**
```bash
# Renew certificates
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

## 🎯 Performance Optimization

### For High Volume Testing
- Increase gunicorn workers in systemd service
- Add database connection pooling
- Set up Redis for caching
- Use PostgreSQL instead of SQLite

### For Multiple Sites
- Configure nginx virtual hosts
- Use separate databases per site
- Implement domain-based routing
- Set up centralized logging

## 📞 Support

- 📖 **Documentation**: Check README.md and PROJECT_SUMMARY.md
- 🐛 **Issues**: Review logs in `/opt/ai-ethics/logs/`
- 🔍 **Debugging**: Use health check endpoints and monitoring scripts
- 📊 **Data Issues**: Verify database integrity with sqlite3 commands

---

**🎉 You're now ready to monitor AI ethics at scale!** 

Start by running the demo, then integrate your AI models for real-world ethical monitoring.
