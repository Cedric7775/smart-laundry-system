# 🚀 Smart Laundry - Deployment & Production Guide

**Last Updated:** March 29, 2026  
**Status:** Production Ready  
**Version:** 1.0

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Variables](#environment-variables)
3. [Local Development](#local-development)
4. [Production Deployment](#production-deployment)
5. [Cloud Platform Setup](#cloud-platform-setup)
6. [Troubleshooting](#troubleshooting)
7. [Architecture Overview](#architecture-overview)

---

## 🎯 Quick Start

### Local Development (Immediate)

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python backend.py

# Output confirms server running on http://localhost:5000
✅ Server running on http://0.0.0.0:5000
🔑 Environment: DEVELOPMENT (DEBUG ON)
```

### Production Deployment (Cloud)

```bash
# Backend auto-detects environment and runs in production mode
# PORT comes from cloud platform (Render auto-assigns)
# DEBUG defaults to OFF
# CORS allows all origins (configure in production)
```

---

## 🔧 Environment Variables

### Required for Production

| Variable         | Default                                  | Use Case                            | Example                                   |
| ---------------- | ---------------------------------------- | ----------------------------------- | ----------------------------------------- |
| `PORT`           | `5000`                                   | HTTP server port                    | `5000` (local), auto on Render            |
| `HOST`           | `0.0.0.0`                                | Network interface to listen on      | `0.0.0.0` (production), `localhost` (dev) |
| `DEBUG`          | `False`                                  | Enable Flask debug mode             | `False` (production), `true` (dev)        |
| `JWT_SECRET_KEY` | `'your-secret-key-change-in-production'` | JWT token secret ⚠️ **CHANGE THIS** | `sk_live_4eC39HqLyjWDarhtT1ZdV7dc`        |

### Optional Environment Variables

| Variable       | Default        | Use Case                 | Example                    |
| -------------- | -------------- | ------------------------ | -------------------------- |
| `DATABASE`     | `./laundry.db` | SQLite database path     | `/tmp/laundry.db`          |
| `CORS_ORIGINS` | `*`            | Allowed frontend domains | `https://smartlaundry.com` |

### Setting Environment Variables

**Option 1: Render.com (Recommended)**

1. Go to Render Dashboard → Your Service
2. Click "Environment" tab
3. Add variables:
   - `JWT_SECRET_KEY`: Set to strong random string
   - `DEBUG`: Leave as `False`
4. Service auto-restarts with new variables

**Option 2: Local with `.env` file** (Not recommended for production)

```bash
# Create .env file
PORT=5000
DEBUG=true
JWT_SECRET_KEY=dev-secret-key

# Load before running
export $(cat .env | xargs)
python backend.py
```

**Option 3: Direct command line**

```bash
export PORT=5000
export DEBUG=false
export JWT_SECRET_KEY=production-secret-key
python backend.py
```

---

## 💻 Local Development

### Setup

```bash
# 1. Clone or navigate to project
cd /path/to/smart-laundry

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run backend (automatically uses localhost:5000)
python backend.py

# Expected output:
# ============================================================
# 🚀 Smart Laundry Python Backend Starting...
# ============================================================
# ✅ Server running on http://0.0.0.0:5000
# 🔑 Environment: DEVELOPMENT (DEBUG ON)
# 📝 API Documentation:
```

### Testing Locally

**1. Backend API Test**

```bash
# Terminal 1: Start backend
python backend.py

# Terminal 2: Test API
curl http://localhost:5000/api/services

# Expected: Returns JSON list of services or empty array
```

**2. Frontend Test**

```bash
# Open in browser
http://localhost:5000/index.html

# Or create simple Python HTTP server for static files:
python -m http.server 8000

# Open browser
http://localhost:8000/index.html
```

**3. Full Integration Test**

- Open http://localhost:5000/index.html
- Click "Book Now"
- Try booking a service (API calls should work)
- Check browser console for errors (F12)

---

## 🌍 Production Deployment

### Pre-Deployment Checklist

- [ ] Change `JWT_SECRET_KEY` to strong random value
- [ ] Set `DEBUG=false`
- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Test locally: `python backend.py`
- [ ] Update CORS origins if restricting to specific domain
- [ ] Verify database file location (writeable path)
- [ ] Check all API endpoints respond correctly

### Code Changes Made for Production

1. **Backend (backend.py)**
   - ✅ Uses `os.getenv('PORT')` instead of hardcoded `5000`
   - ✅ Uses `os.getenv('HOST')` defaults to `0.0.0.0` (production-ready)
   - ✅ Debug mode controlled by `DEBUG` env var
   - ✅ CORS configured for all origins (secure for specific domains)
   - ✅ Startup prints show environment (DEV vs PROD)

2. **Frontend (script.js, admin.html, dashboard.html)**
   - ✅ Replaced hardcoded `http://localhost:5000/api`
   - ✅ Now detects if running on localhost (uses port 5000)
   - ✅ On production, uses relative URL (smarts): `/api`
   - ✅ Works with any domain automatically

---

## ☁️ Cloud Platform Setup

### Option 1: Render.com (Recommended - Easy)

**Create a New Web Service:**

1. Sign up at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repo (or use "Public Git Repository")
   - Repository URL: `https://github.com/your-repo/smart-laundry.git`
   - Branch: `main`

4. Configure Service:
   - **Name:** `smart-laundry-backend`
   - **Region:** Choose closest to users (e.g., Frankfurt, Singapore)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python backend.py`

5. Environment Variables (click "Advanced")
   - `JWT_SECRET_KEY`: Generate strong key (use https://generate.plus/en/hash)
   - `DEBUG`: `false`

6. Click "Create Web Service"
7. Wait for deployment (2-3 minutes)
8. Copy URL: `https://smart-laundry-backend.onrender.com`

**Frontend Configuration:**

```javascript
// Frontend auto-detects production and uses /api
// Update if domain is different from backend domain
// Alternatively, set backend URL explicitly
const API_BASE_URL = "https://smart-laundry-backend.onrender.com/api";
```

### Option 2: Heroku (Also Easy)

1. Sign up at [heroku.com](https://heroku.com)
2. Create new app: `heroku create smart-laundry-backend`
3. Push code: `git push heroku main`
4. Set env vars:
   ```bash
   heroku config:set JWT_SECRET_KEY=your-strong-key
   heroku config:set DEBUG=false
   heroku logs --tail  # Watch deployment
   ```

### Option 3: DigitalOcean App Platform

1. Visit [app.digitalocean.com](https://app.digitalocean.com)
2. Click "Create" → "App"
3. Connect GitHub repo
4. Detect Python automatically
5. Set environment variables in dashboard
6. Deploy

### Option 4: AWS, Azure, Google Cloud

All require more configuration. Use same principles:

- Set `PORT` and `HOST` env vars
- Install dependencies from `requirements.txt`
- Start with: `python backend.py`

---

## 🐛 Troubleshooting

### Issue: "Port already in use"

```bash
# Solution: Change PORT
export PORT=5001
python backend.py

# Or find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows
# Kill process if needed
```

### Issue: "Database connection failed"

```bash
# Ensure database path is writeable
ls -l laundry.db  # Check permissions

# If permission denied:
chmod 644 laundry.db  # Make writeable

# Or use temp directory:
export DATABASE=/tmp/laundry.db
python backend.py
```

### Issue: "CORS error - blocked by browser"

```
Access to fetch at 'http://api.example.com/...' from origin 'http://frontend.example.com'
has been blocked by CORS policy
```

**Solution:** Update CORS in backend.py:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://frontend.example.com", "https://www.frontened.example.com"],
        "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Issue: "No module named 'flask'"

```bash
# Solution: Install dependencies
pip install -r requirements.txt

# Verify:
python -c "import flask; print(flask.__version__)"
```

### Issue: "JWT token expired or invalid"

```
Error: 401 Unauthorized - Token invalid or expired
```

**Possible causes:**

1. `JWT_SECRET_KEY` differs between frontend/backend
2. Token created with old key, tried with new key
3. Session/token actually expired (30 days default)

**Solution:**

- Verify `JWT_SECRET_KEY` is same across all instances
- Clear browser cookies/localStorage: `localStorage.clear()`
- Re-login/register to get new token

### Issue: "Frontend shows 'Cannot connect to API'"

```bash
# Check if backend is running
curl https://your-backend-url.onrender.com/api/services

# Should return: []  (empty array) or list of services

# If fails, check:
1. Backend URL is correct in frontend
2. Backend is actually deployed and running
3. CORS is enabled (check for CORS error in browser console)
4. Firewall/network allows connection
```

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   CLOUD PLATFORM                        │
│                                                         │
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │  Backend (Python)    │    │  Frontend (Static)   │  │
│  │  ✅ PORT env var     │◄──►│  ✅ Dynamic API URL  │  │
│  │  ✅ debug=false      │    │  ✅ auto-detects     │  │
│  │  ✅ CORS enabled     │    │                      │  │
│  │  ✅ JWT handler      │    │  script.js           │  │
│  │  ✅ SQLite DB        │    │  admin.html          │  │
│  │                      │    │  dashboard.html      │  │
│  └──────────────────────┘    └──────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ▲
         │ Environment Variables (Git + Platform)
         │
         └─ PORT, DEBUG, JWT_SECRET_KEY, HOST
```

### API Endpoints (All Functional)

**Authentication:**

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

**Bookings:**

- `POST /api/bookings` - Create new booking
- `GET /api/bookings` - Get all bookings (admin)
- `GET /api/bookings/my-bookings` - Get user bookings
- `PATCH /api/bookings/<id>` - Update booking status
- `GET /api/bookings/<id>/status-logs` - Get status history
- `POST /api/bookings/<id>/status-logs` - Log status change

**Services:**

- `GET /api/services` - List all services
- `POST /api/services` - Create service (admin)
- `PATCH /api/services/<id>` - Update service (admin)

**Addresses:**

- `GET /api/addresses` - Get user addresses
- `POST /api/addresses` - Save address
- `PATCH /api/addresses/<id>` - Update address
- `DELETE /api/addresses/<id>` - Delete address

**Contacts:**

- `POST /api/contacts` - Submit contact form
- `GET /api/contacts` - Get all contacts (admin)
- `PATCH /api/contacts/<id>` - Update contact (admin)

---

## 📊 Deployment Checklist

### Pre-Deployment

- [ ] All code committed to Git
- [ ] requirements.txt includes all packages
- [ ] JWT_SECRET_KEY set to strong value
- [ ] DEBUG set to `false`
- [ ] CORS origins configured (or allow all for public API)
- [ ] .env file NOT committed to Git (if using)
- [ ] Database permissions verified

### During Deployment

- [ ] Service builds successfully (check logs)
- [ ] Environment variables set correctly
- [ ] Backend starts without errors
- [ ] Frontend connects to backend

### Post-Deployment

- [ ] Test API endpoint manually (curl/Postman)
- [ ] Test frontend functionality
- [ ] Check browser console for errors
- [ ] Verify JWT token works
- [ ] Monitor logs for warnings/errors

---

## 🔐 Security Reminders

⚠️ **CRITICAL FOR PRODUCTION:**

1. **Change JWT_SECRET_KEY**
   - Default value in code is for development only
   - Use strong random string (min 32 chars)
   - Generate: https://generate.plus/en/hash

2. **Set DEBUG=false**
   - Never leave debug mode on in production
   - Exposes sensitive error information

3. **CORS Configuration**
   - Default allows all origins (development)
   - In production, restrict to your frontend domain
   - Example: `"origins": ["https://smartlaundry.com"]`

4. **HTTPS Only**
   - Render, Heroku, etc. provide HTTPS automatically
   - Never send tokens over HTTP
   - Browser will block insecure requests

5. **Environment Variables**
   - Never commit secrets to Git
   - Use platform's secret management (Render, Heroku)
   - Rotate secrets periodically

---

## 📞 Support & Monitoring

### Logs on Render

```bash
# View logs in real-time
# Render Dashboard → Your Service → Logs tab
# Shows all startup messages and errors
```

### Common Log Messages

✅ **Good - Service Started**

```
🚀 Smart Laundry Python Backend Starting...
✅ Server running on http://0.0.0.0:5000
🔑 Environment: PRODUCTION (DEBUG OFF)
```

❌ **Bad - Environment Error**

```
Error: Cannot connect to database at /path/to/laundry.db
→ Solution: Check database path and permissions
```

❌ **Bad - Port Conflict**

```
Error: Address already in use
→ Solution: PORT already taken, or old process still running
```

---

## 🔄 Deployment Workflow (Git → Cloud)

1. **Make Changes Locally**

   ```bash
   git add .
   git commit -m "feat: update delivery workflow"
   ```

2. **Push to GitHub**

   ```bash
   git push origin main
   ```

3. **Cloud Platform Auto-Deploys**
   - Render/Heroku detects push
   - Runs `pip install -r requirements.txt`
   - Runs `python backend.py`
   - Service goes live (auto-restart)

4. **Verify Deployment**
   ```bash
   curl https://your-service.onrender.com/api/services
   ```

---

## 📈 Performance Tips

1. **Database Optimization**
   - Add indexes for frequently queried fields
   - Regular backups (download from platform)
   - Consider PostgreSQL for larger scale (Render free tier)

2. **CORS Performance**
   - Specify allowed origins instead of `*`
   - Reduces preflight requests

3. **JWT Token Size**
   - Current tokens are small (< 1KB)
   - No performance issue at scale

4. **Frontend Caching**
   - Static files cached by browser
   - API responses cache-friendly headers (add as needed)

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask Deployment](https://flask.palletsprojects.com/deployment/)
- [CORS & Browser Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

## ✅ Summary

### What's Ready for Production

✅ Backend uses environment variables (PORT, DEBUG, HOST)  
✅ Frontend auto-detects API endpoint  
✅ CORS enabled for production  
✅ JWT authentication configured  
✅ Database auto-initialized on startup  
✅ Error logging in place  
✅ All API endpoints functional  
✅ Mobile-responsive dashboard  
✅ 4-stage delivery workflow

### Next Steps

1. **Deploy to Cloud:**
   - Push to GitHub
   - Create service on Render/Heroku
   - Set JWT_SECRET_KEY env var
   - Deploy!

2. **Monitor:**
   - Watch logs for errors
   - Test all features
   - Performance metrics

3. **Optimize:**
   - Add security headers
   - Implement rate limiting (if needed)
   - Backup strategy for database

---

**Version:** 1.0  
**Date:** March 29, 2026  
**Status:** Ready for Production Deployment 🚀
