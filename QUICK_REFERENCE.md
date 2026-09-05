# Intelligence Dashboard - Quick Reference

Quick command reference for the Intelligence Dashboard MongoDB project.

## 🚀 Quick Start

### Docker (Recommended)
```bash
cd osnit-project
docker-compose up -d
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:5173
```

### Manual Start
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Make sure MongoDB is running
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Terminal 3: MongoDB (if not running)
mongosh
```

---

## 📝 Essential Commands

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f mongodb
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v

# Restart specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend python script.py
docker-compose exec mongodb mongosh
```

### MongoDB

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/intel_dashboard

# Database operations
use intel_dashboard
show collections
show databases

# Collection operations
db.officers.find()
db.officers.find().pretty()
db.threat_posts.find()
db.threat_posts.count()

# Insert test officer
db.officers.insertOne({
  email: "test@example.com",
  hashed_password: "bcrypt_hash",
  clearance_level: 5,
  is_active: true,
  created_at: new Date()
})

# Update document
db.threat_posts.updateOne(
  {_id: ObjectId("...")},
  {$set: {is_resolved: true}}
)

# Delete document
db.threat_posts.deleteOne({_id: ObjectId("...")})

# Drop collection
db.officers.drop()

# Create index
db.threat_posts.createIndex({timestamp: -1})
```

### Backend

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
uvicorn main:app --port 8001

# Check Python syntax
python -m py_compile *.py

# Check specific file
python -c "import database; print('OK')"
```

### Frontend

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Clear npm cache
npm cache clean --force
```

---

## 🔍 Testing & Verification

### Test Backend API

```bash
# Check API health
curl http://localhost:8000/docs

# Create officer
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

# Create threat post (replace TOKEN)
curl -X POST http://localhost:8000/threats \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Potential security threat detected",
    "platform": "twitter",
    "threat_level": 3,
    "panic_score": 45.0
  }'

# Get threat posts
curl -X GET "http://localhost:8000/threats?skip=0&limit=10" \
  -H "Authorization: Bearer TOKEN"
```

### Test MongoDB Connection

```bash
# From backend directory
python -c "
import asyncio
from motor.motor_asyncio import AsyncClient

async def test():
    client = AsyncClient('mongodb://localhost:27017')
    result = await client.admin.command('ping')
    print('MongoDB connection:', result)

asyncio.run(test())
"
```

### Test Frontend

```bash
# Check if running
curl http://localhost:5173

# Check in browser
# Open http://localhost:5173
# F12 to open developer console
# Look for any errors in Console tab
```

---

## 🔧 Environment Variables

### Backend (.env)

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=intel_dashboard

# Security
JWT_SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_GROUP_ID=intel-dashboard-stream-processor
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000
```

---

## 📊 Database Collections

### Officers Collection
```json
{
  "_id": ObjectId("..."),
  "email": "officer@example.com",
  "hashed_password": "bcrypt_hash_here",
  "clearance_level": 5,
  "is_active": true,
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```

### Threat Posts Collection
```json
{
  "_id": ObjectId("..."),
  "content": "Threat description",
  "platform": "twitter",
  "threat_level": 4,
  "panic_score": 75.5,
  "timestamp": ISODate("2024-01-01T12:30:00Z"),
  "is_resolved": false
}
```

---

## 🐛 Troubleshooting

### MongoDB Won't Connect
```bash
# Check if running
mongosh

# Check connection URL
echo $MONGODB_URL

# Verify port
# Windows: netstat -ano | findstr 27017
# Linux: lsof -i :27017
```

### Port Already in Use
```bash
# Find process on port 8000
# Windows: netstat -ano | findstr 8000
# Linux: lsof -i :8000

# Kill process or use different port
uvicorn main:app --port 8001
```

### Module Not Found
```bash
# Verify venv is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check specific module
pip list | grep motor
```

### Docker Issues
```bash
# Remove all containers
docker-compose down

# Rebuild images
docker-compose up -d --build

# Check service status
docker-compose ps

# View specific logs
docker-compose logs backend -f --tail=50
```

---

## 📚 API Endpoints Quick Reference

### Authentication
- `POST /login` - Login (email & password)
- `POST /officers` - Create officer
- `GET /officers/me` - Get current officer

### Threats
- `POST /threats` - Create threat post
- `GET /threats` - List threats (with filtering)
- `GET /threats/{id}` - Get specific threat
- `PATCH /threats/{id}` - Update threat

### WebSocket
- `WS /ws/live-feed` - Real-time threat feed (JWT required)

---

## 📁 Important Files

```
backend/
├── main.py           # FastAPI app & routes
├── models.py         # MongoDB Pydantic models
├── schemas.py        # Request/response schemas
├── database.py       # MongoDB connection
├── crud.py           # Database operations
├── auth.py           # JWT & authentication
├── requirements.txt  # Python dependencies
└── .env             # Configuration (DO NOT COMMIT)

frontend/
├── src/App.jsx       # Main component
├── src/Login.jsx     # Login page
├── src/Dashboard.jsx # Dashboard page
├── src/AuthContext.jsx # Auth hooks
├── package.json      # npm dependencies
└── vite.config.js    # Vite configuration

docker-compose.yml    # Multi-container orchestration
.env.example          # Environment template
README.md             # Project overview
SETUP.md              # Detailed setup guide
```

---

## 🔗 Useful Links

- **FastAPI Docs**: http://localhost:8000/docs (Swagger)
- **MongoDB Docs**: https://docs.mongodb.com/
- **Motor (Async MongoDB)**: https://motor.readthedocs.io/
- **Pydantic**: https://docs.pydantic.dev/
- **React**: https://react.dev/
- **Vite**: https://vitejs.dev/

---

## 💡 Tips

- Use `--reload` flag with uvicorn for auto-restart on changes
- Check browser console (F12) for frontend errors
- Use `docker-compose logs -f` to monitor all services
- MongoDB Compass GUI for visual database exploration
- Postman or Insomnia for API testing

---

**Last Updated:** 2024
**Status:** MongoDB Configuration Complete
