# 🐳 Portainer Deployment Instructions
## Replace Static Placeholder with AI Ethics Testing Framework

### 🎯 **Objective**
Replace the static "Velkommen til skyforskning" page in container `1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430` with the full AI Ethics Testing Framework.

---

## ⚡ **Method 1: Quick Container Update (Recommended)**

### 1. **Access Portainer**
- Go to your Portainer interface
- Navigate to **Containers**
- Find container ID: `1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430`

### 2. **Stop and Duplicate Container**
- Click on the container name
- Click **"Stop"** to stop the container
- Click **"Duplicate/Edit"**

### 3. **Update Container Configuration**

**Basic Settings:**
- **Name:** `ai-ethics-framework-production`
- **Image:** `python:3.11-slim`

**Command & Logging:**
- **Command:** 
```bash
sh -c "apt-get update && apt-get install -y curl && pip install flask flask-cors gunicorn && cd /app && python3 -m gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 120 run_app:app"
```

**Volumes:**
- **Add Volume Mapping:**
  - **Container path:** `/app`
  - **Host path:** `/home/skyforskning.no/forskning`
  - **Type:** Bind mount

**Environment Variables:**
- `PYTHONPATH=/app`
- `FLASK_ENV=production`

**Network & Ports:**
- **Port mapping:** `8020:80` (should already exist)
- **Restart policy:** `Unless stopped`

**Advanced (Optional):**
- **Working directory:** `/app`
- **User:** `1000` (for security)

### 4. **Deploy**
- Click **"Deploy the container"**
- Wait 2-3 minutes for dependencies to install and application to start
- Monitor logs for "Starting gunicorn" message

---

## 🔄 **Method 2: Docker Command Line (Alternative)**

If you have Docker CLI access:

```bash
# Stop and remove the old container
docker stop 1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430
docker rm 1a0c86120b1c1a346e71df887e4fdda8baa9f8e482fdeb277cb7bfa7585f9430

# Create new container
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

---

## 🧪 **Testing & Verification**

### After deployment, test these URLs:

1. **HTTP:** http://forskning.skycode.no
2. **HTTPS:** https://forskning.skycode.no

### **Expected Result:**
- ❌ **Before:** "Velkommen til skyforskning"
- ✅ **After:** "AI Ethics Testing Dashboard" with full interface

### **Health Check:**
```bash
curl -I https://forskning.skycode.no
# Should return HTTP 200 and show HTML content
```

---

## 🚨 **Troubleshooting**

### **Container Won't Start:**
1. Check container logs in Portainer
2. Verify volume path `/home/skyforskning.no/forskning` exists and is accessible
3. Ensure port 8020 is not used by other containers

### **Application Not Loading:**
1. Wait 2-3 minutes for dependencies to install
2. Check logs for "Starting gunicorn" message
3. Verify all Python files are in the mounted directory

### **502 Bad Gateway:**
1. Application is still starting up - wait longer
2. Check if gunicorn process is running in container logs
3. Restart the container if needed

### **Log Commands:**
```bash
# View container logs
docker logs ai-ethics-framework-production

# Enter container for debugging
docker exec -it ai-ethics-framework-production bash
```

---

## 📊 **Configuration Summary**

| Setting | Value |
|---------|-------|
| **Container Name** | ai-ethics-framework-production |
| **Image** | python:3.11-slim |
| **Port Mapping** | 8020:80 |
| **Volume Mount** | /home/skyforskning.no/forskning:/app |
| **Working Directory** | /app |
| **Environment** | PYTHONPATH=/app, FLASK_ENV=production |
| **Command** | Gunicorn with auto-dependency installation |
| **Restart Policy** | Unless stopped |

---

## ✅ **Success Indicators**

1. **Container Status:** Running (green in Portainer)
2. **Website Response:** AI Ethics Testing Dashboard loads
3. **Health Check:** HTTP 200 responses
4. **Logs:** "Starting gunicorn" and worker processes
5. **Functionality:** Can navigate dashboard features

---

## 📞 **Next Steps After Deployment**

1. **Test all dashboard features**
2. **Run ethical dilemma tests**
3. **Verify database functionality**
4. **Check API endpoints**
5. **Monitor performance and logs**

The static placeholder page will be completely replaced with your AI Ethics Testing Framework! 🎉
