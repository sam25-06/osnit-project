# Intelligence Dashboard - MongoDB Setup Guide

Complete setup instructions for the Intelligence Dashboard with MongoDB architecture.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Manual Setup](#manual-setup)
4. [Environment Configuration](#environment-configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### All Platforms

- **Git**: For version control
- **2GB RAM** minimum available
- **5GB** disk space

### Option 1: Docker Setup (Recommended)

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose 2.0+

### Option 2: Manual Setup

**Backend:**
- Python 3.10+
- MongoDB 7+
- pip (Python package manager)

**Frontend:**
- Node.js 16+
- npm 7+

### Download Links

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [MongoDB Community](https://www.mongodb.com/try/download/community)
- [Python](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/)

---

## Quick Start with Docker

### Step 1: Prepare Project

```bash
cd osnit-project
```

### Step 2: Create Environment File

```bash
cd backend
cp .env.example .env
cd ..
```

### Step 3: Start Services

```bash
# Build and start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs (optional)
docker-compose logs -f
```

### Step 4: Access Services

- **Backend API**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **MongoDB**: mongodb://localhost:27017

### Step 5: Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove data volumes (WARNING: deletes database)
docker-compose down -v
```

---

## Manual Setup

### Backend Setup

#### 1. Navigate to Backend

```bash
cd osnit-project/backend
```

#### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

# If execution policy error occurs:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Create Environment File

```bash
cp .env.example .env
```

Edit `.env`:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=intel_dashboard
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-12345
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### 5. Install MongoDB

**Windows - Using Installer:**

1. Download: https://www.mongodb.com/try/download/community
2. Run installer and follow prompts
3. MongoDB starts automatically as a service
4. Verify: Open PowerShell and run:
   ```powershell
   mongosh
   ```

**Windows - Using Chocolatey:**

```powershell
choco install mongodb-community
```

**Windows - Using Winget:**

```powershell
winget install MongoDB.Server
```

**macOS - Using Homebrew:**

```bash
brew install mongodb-community
brew services start mongodb-community
mongosh  # Verify connection
```

**Linux - Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongod
mongosh  # Verify connection
```

**Any Platform - Using Docker:**

```bash
docker run -d -p 27017:27017 --name mongodb mongo:7-alpine
```

#### 6. Verify MongoDB Connection

```bash
# Connect to MongoDB
mongosh

# In MongoDB shell:
use intel_dashboard
show collections
exit
```

#### 7. Start Backend Server

```bash
# Ensure virtual environment is activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Access backend at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### Frontend Setup

#### 1. Navigate to Frontend

```bash
cd osnit-project/frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Start Development Server

```bash
npm run dev
```

Expected output:
```
  VITE v8.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

Access frontend at: http://localhost:5173

---

## Environment Configuration

### Backend Environment Variables

**File:** `backend/.env`

**Required Variables:**

```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=intel_dashboard

# Security
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Optional Variables:**

```bash
# For Kafka stream processing (if enabled)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_GROUP_ID=intel-dashboard-stream-processor
```

### Frontend Environment Variables

**File:** `frontend/.env` (optional)

```bash
# API URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

---

## Verification

### Complete System Check

#### Check MongoDB

```bash
mongosh mongodb://localhost:27017/intel_dashboard

# In MongoDB shell:
db.adminCommand("ping")
show collections
```

#### Check Backend

```bash
# Test API health
curl http://localhost:8000/docs

# Create test officer (in Swagger UI or with curl)
curl -X POST http://localhost:8000/officers \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "clearance_level": 5
  }'

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123"
```

#### Check Frontend

1. Open http://localhost:5173
2. Verify page loads
3. Test login with created credentials

---

## Troubleshooting

### MongoDB Connection Issues

**Problem:** "Could not connect to MongoDB"

**Solutions:**

1. Verify MongoDB is running:
   ```bash
   mongosh mongodb://localhost:27017
   ```

2. Check MONGODB_URL in `.env`:
   ```bash
   # Local: mongodb://localhost:27017
   # Docker: mongodb://mongodb:27017
   ```

3. Verify port 27017 is open:
   ```bash
   # Windows
   netstat -ano | findstr 27017
   
   # Linux
   lsof -i :27017
   ```

4. Restart MongoDB:
   ```bash
   # Docker
   docker-compose restart mongodb
   
   # Windows Service
   Restart-Service MongoDB
   
   # Linux
   sudo systemctl restart mongod
   ```

### Backend Won't Start

**Problem:** "Port 8000 already in use"

**Solutions:**

```bash
# Find process on port 8000
# Windows: netstat -ano | findstr 8000
# Linux: lsof -i :8000

# Use different port
uvicorn main:app --port 8001
```

**Problem:** "Module not found: motor"

**Solutions:**

```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Won't Start

**Problem:** "npm: command not found"

**Solutions:**

```bash
# Verify Node installation
node --version
npm --version

# If needed, install Node from https://nodejs.org/
```

**Problem:** "Port 5173 already in use"

**Solutions:**

```bash
npm run dev -- --port 5174
```

### API Not Responding from Frontend

**Problem:** "Failed to fetch"

**Solutions:**

1. Verify backend is running:
   ```bash
   curl http://localhost:8000/docs
   ```

2. Check frontend environment:
   ```bash
   # Check browser console (F12)
   # Look for CORS or connection errors
   ```

3. Verify VITE_API_URL in frontend `.env` is correct

4. Restart services

### Docker Issues

**Problem:** "docker: command not found"

**Solution:**
Install Docker Desktop from https://www.docker.com/products/docker-desktop

**Problem:** "docker-compose: command not found"

**Solution:**
Use Docker Compose V2:
```bash
docker compose --version
```

**Problem:** Service exits immediately

**Solution:**
```bash
# Check logs
docker-compose logs mongodb
docker-compose logs backend
docker-compose logs frontend

# Rebuild
docker-compose down
docker-compose up -d --build
```

### JWT/Authentication Issues

**Problem:** "Could not validate credentials"

**Solutions:**

1. Verify JWT_SECRET_KEY in `.env`:
   ```bash
   # On Windows PowerShell
   Get-Content .env | Select-String JWT_SECRET_KEY
   ```

2. Check token hasn't expired (30 minutes default)

3. Verify Authorization header format:
   ```bash
   Authorization: Bearer <your_token_here>
   ```

4. Test login again

### Data Loss on Restart

**Problem:** Data disappears after restart

**Solutions:**

1. Verify MongoDB data directory:
   ```bash
   # Windows: C:\Program Files\MongoDB\Server\7.0\data
   # Linux: /var/lib/mongodb
   ```

2. Check Docker volume persistence:
   ```bash
   docker volume ls
   docker inspect mongodb_data
   ```

3. Don't use `docker-compose down -v` (removes data)

---

## Development Tips

### Useful Commands

**Backend:**

```bash
# Run with auto-reload
uvicorn main:app --reload

# Run specific file compilation check
python -m py_compile backend/*.py

# View MongoDB data
mongosh mongodb://localhost:27017/intel_dashboard
```

**Frontend:**

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

**Docker:**

```bash
# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python -c "import motor; print('OK')"

# Restart specific service
docker-compose restart backend

# Remove everything (WARNING: deletes data)
docker-compose down -v
```

### MongoDB Shell Tips

```bash
mongosh mongodb://localhost:27017/intel_dashboard

# List all databases
show databases

# Use specific database
use intel_dashboard

# List collections
show collections

# Query documents
db.officers.find()
db.threat_posts.find()

# Count documents
db.threat_posts.count_documents({})

# View specific document
db.threat_posts.findOne()

# Update document
db.threat_posts.updateOne({_id: ObjectId("...")}, {$set: {is_resolved: true}})

# Delete document
db.threat_posts.deleteOne({_id: ObjectId("...")})
```

---

## Next Steps

1. **Create Initial Data:**
   - Use Swagger UI to create officer accounts
   - Create and update threat posts

2. **Test WebSocket:**
   - Connect to `/ws/live-feed` endpoint
   - Create threat posts to see real-time updates

3. **Review Logs:**
   - Monitor MongoDB queries
   - Check backend/frontend console
   - Verify authentication flow

4. **Customize:**
   - Adjust JWT expiration
   - Modify clearance levels
   - Update threat scoring logic

---

## Getting Help

1. **Check Logs:**
   ```bash
   # Backend logs
   docker-compose logs backend
   
   # MongoDB logs
   docker-compose logs mongodb
   ```

2. **Verify Connectivity:**
   ```bash
   # MongoDB
   mongosh mongodb://localhost:27017
   
   # Backend
   curl http://localhost:8000/docs
   ```

3. **Review Documentation:**
   - [MongoDB Docs](https://docs.mongodb.com/)
   - [FastAPI Docs](https://fastapi.tiangolo.com/)
   - [Motor Docs](https://motor.readthedocs.io/)

---

**Last Updated:** 2024
**Status:** MongoDB Configuration Complete
