# Intelligence Dashboard

A real-time intelligence threat monitoring system built with FastAPI (backend), React (frontend), and MongoDB (persistent document storage).

## 📋 Project Overview

The Intelligence Dashboard is a modern, full-stack application designed for security professionals and intelligence officers to monitor, analyze, and respond to threat intelligence from multiple social media platforms in real-time.

### Key Features
- **Authentication & Authorization**: JWT-based authentication with clearance level controls
- **Real-time Threat Monitoring**: WebSocket-based live feed for threat updates
- **Threat Analytics**: Automatic threat level scoring and panic index calculation
- **Stream Processing**: Kafka consumer for processing threats from social platforms (optional)
- **Document Storage**: MongoDB for flexible, scalable threat data persistence
- **Role-based Access Control**: Support for multiple clearance levels

## 📁 Project Structure

```
osnit-project/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # FastAPI app, routes, WebSocket handlers
│   ├── models.py              # Pydantic models for MongoDB documents
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── database.py            # MongoDB connection and collection management
│   ├── auth.py                # JWT authentication & authorization
│   ├── crud.py                # Database CRUD operations
│   ├── stream_processor.py    # Kafka consumer for threat stream processing
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container image
│   ├── .env.example           # Environment configuration template
│   └── README.md              # Backend-specific documentation
│
└── frontend/                   # React + Vite frontend
    ├── src/
    │   ├── main.jsx           # React entry point
    │   ├── App.jsx            # Main App component
    │   ├── App.css            # Global styles
    │   ├── Login.jsx          # Login page component
    │   ├── Dashboard.jsx      # Main dashboard component
    │   ├── AuthContext.jsx    # Authentication context & hooks
    │   ├── index.css          # Index styles
    │   └── assets/            # Static assets
    ├── public/                # Public static files
    ├── index.html             # HTML entry point
    ├── package.json           # npm dependencies
    ├── vite.config.js         # Vite configuration
    ├── Dockerfile             # Frontend container image
    └── README.md              # Frontend-specific documentation
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: MongoDB 7 with Motor async driver
- **Authentication**: JWT with Python-Jose
- **Data Validation**: Pydantic 2.5+
- **Password Hashing**: Passlib with bcrypt
- **Streaming** (Optional): Apache Kafka with AIOKafka

### Frontend
- **Framework**: React 19.2+
- **Build Tool**: Vite 8.2+
- **Type Checking**: TypeScript (via Vite)
- **HTTP Client**: Fetch API

### Infrastructure
- **Database**: MongoDB 7
- **Containerization**: Docker & Docker Compose

## 🚀 Getting Started

### Quick Start with Docker (Recommended)

```bash
# Start all services (MongoDB, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This will start:
- MongoDB on port 27017
- Backend FastAPI on port 8000
- Frontend development server on port 5173

### Prerequisites (For Manual Setup)

**Backend:**
- Python 3.10+
- MongoDB 7+ (or Docker)
- Kafka 3.0+ (optional, for stream processing)

**Frontend:**
- Node.js 16+ and npm 7+

### Backend Setup (Manual)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection details
   ```

5. **Start MongoDB** (if not using Docker):
   ```bash
   # On Windows with MongoDB installed:
   mongod
   
   # Or use Docker:
   docker run -d -p 27017:27017 --name mongodb mongo:7-alpine
   ```

6. **Run the backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The backend will be available at http://localhost:8000
- API Documentation: http://localhost:8000/docs (Swagger UI)
- Alternative docs: http://localhost:8000/redoc (ReDoc)

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:5173

## 📚 API Documentation

### Authentication
- **POST /login** - Authenticate with email and password
  - Returns: `{access_token, token_type, expires_in}`
  - Protected endpoints use: `Authorization: Bearer <token>`

### Officers (Security Personnel)
- **POST /officers** - Create new officer (admin only)
- **GET /officers/me** - Get current officer profile
  - Requires: Valid JWT token

### Threat Intelligence
- **POST /threats** - Create new threat post
  - Requires: Valid JWT token, clearance level 2+
  - Body: `{content, platform, threat_level, panic_score}`

- **GET /threats** - List threat posts with filtering
  - Query params: `skip`, `limit`, `min_threat_level`, `is_resolved`
  - Returns: Paginated threat list

- **GET /threats/{post_id}** - Get specific threat post
- **PATCH /threats/{post_id}** - Update threat post status
  - Body: `{threat_level, panic_score, is_resolved}`

### WebSocket
- **WS /ws/live-feed** - Real-time threat feed
  - Requires: JWT token via query param or headers
  - Broadcasts threat updates to connected clients

## 🗄️ MongoDB Collections

### Officers Collection
```json
{
  "_id": ObjectId,
  "email": "officer@example.com",
  "hashed_password": "bcrypt_hash",
  "clearance_level": 5,
  "is_active": true,
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```
**Indexes:**
- `email` (unique)
- `is_active`

### Threat Posts Collection
```json
{
  "_id": ObjectId,
  "content": "Threat description...",
  "platform": "twitter",
  "threat_level": 4,
  "panic_score": 75.5,
  "timestamp": ISODate("2024-01-01T12:30:00Z"),
  "is_resolved": false
}
```
**Indexes:**
- `platform`
- `threat_level`
- `is_resolved`
- `timestamp` (for sorting)

## 🔒 Security Notes

- **Passwords** are hashed with bcrypt
- **JWT tokens** expire after 30 minutes (configurable)
- **Clearance levels** control access to sensitive endpoints
- **MongoDB** connection uses local connection by default; configure credentials in `.env`
- Always use HTTPS in production
- Change `JWT_SECRET_KEY` in `.env` for production

## 🛠️ Development Workflow

### Running Tests
```bash
# Backend tests (if configured)
cd backend
pytest
```

### Monitoring Backend Health
```bash
# Check API health
curl http://localhost:8000/docs
```

### Viewing MongoDB Data
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/intel_dashboard

# List collections
show collections

# Query officers
db.officers.find()

# Query threat posts
db.threat_posts.find()
```

## 📖 Additional Documentation

- [Backend README](./backend/README.md) - Backend-specific setup and API details
- [Frontend README](./frontend/README.md) - Frontend-specific setup and component guide
- [SETUP.md](./SETUP.md) - Detailed setup instructions
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick command reference

## ❓ Troubleshooting

### MongoDB Connection Issues
```bash
# Test MongoDB connection
mongosh mongodb://localhost:27017

# Check if MongoDB is running
# Windows: mongosh localhost:27017
# Linux: sudo systemctl status mongod
```

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | grep -E "motor|fastapi|pydantic"

# Check .env file
cat .env
```

### Frontend Won't Load
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Check Node version
node --version  # Should be 16+

# Clear npm cache
npm cache clean --force
```

## 📝 License

This project is provided as-is for educational and security purposes.

## 🤝 Contributing

Contributions are welcome! Please follow the established code patterns and update documentation accordingly.

---

**Last Updated**: 2024
**Status**: Active Development
