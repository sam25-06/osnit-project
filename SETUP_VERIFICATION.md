# Setup Verification Checklist

Use this checklist to verify your development environment is set up correctly.

## ✅ Prerequisites

- [ ] Python 3.10+ installed: `python --version`
- [ ] Node.js 16+ installed: `node --version`
- [ ] npm 7+ installed: `npm --version`
- [ ] Git installed: `git --version`
- [ ] Docker (optional but recommended): `docker --version`

## ✅ Project Structure

- [ ] Backend folder exists: `osnit-project/backend/`
- [ ] Frontend folder exists: `osnit-project/frontend/`
- [ ] README.md exists in root
- [ ] SETUP.md exists in root
- [ ] requirements.txt exists in backend/
- [ ] package.json exists in frontend/

## ✅ Backend Setup

- [ ] Python virtual environment created
  ```bash
  cd backend
  python -m venv .venv
  ```

- [ ] Virtual environment activated
  - Windows: `.venv\Scripts\activate`
  - macOS/Linux: `source .venv/bin/activate`
  - Should see `(.venv)` in terminal

- [ ] Dependencies installed
  ```bash
  pip install -r requirements.txt
  ```

- [ ] `.env` file created in `backend/`
  - [ ] Contains `DATABASE_URL`
  - [ ] Contains `REDIS_URL`
  - [ ] Contains `JWT_SECRET_KEY`

- [ ] Database configured
  - [ ] PostgreSQL running
  - [ ] Database `intel_dashboard` exists
  - [ ] Test connection: `psql -U postgres -d intel_dashboard`

- [ ] Redis configured
  - [ ] Redis running
  - [ ] Test connection: `redis-cli ping` (should return PONG)

## ✅ Frontend Setup

- [ ] Navigate to frontend folder
  ```bash
  cd frontend
  ```

- [ ] Dependencies installed
  ```bash
  npm install
  ```

- [ ] `.env` file created with
  - [ ] `VITE_API_URL=http://localhost:8000`

## ✅ Backend Verification

- [ ] Start backend server
  ```bash
  cd backend
  .venv\Scripts\activate  # Windows
  uvicorn main:app --reload
  ```

- [ ] Check for startup messages
  - [ ] No error messages in terminal
  - [ ] "Application startup complete" message visible
  - [ ] Running on http://0.0.0.0:8000

- [ ] API Health Check
  ```bash
  curl http://localhost:8000/health
  ```
  Expected response: `{"status":"ok"}`

- [ ] Access Swagger UI
  - [ ] Open http://localhost:8000/docs
  - [ ] All endpoints visible
  - [ ] "Try it out" buttons work

## ✅ Frontend Verification

- [ ] Start frontend server (new terminal)
  ```bash
  cd frontend
  npm run dev
  ```

- [ ] Check for startup messages
  - [ ] No error messages
  - [ ] "ready in X ms" message visible
  - [ ] Local URL shown (usually http://localhost:5173)

- [ ] Access frontend in browser
  - [ ] Open http://localhost:5173
  - [ ] Page loads without errors
  - [ ] No console errors (F12 → Console tab)

## ✅ Database Verification

- [ ] Connect to database
  ```bash
  psql -U postgres -d intel_dashboard
  ```

- [ ] Check tables exist
  ```sql
  \dt
  ```
  Should show `officers` and `threat_posts` tables

- [ ] Test query
  ```sql
  SELECT COUNT(*) FROM officers;
  ```
  Should return `0` if new database

## ✅ Redis Verification

- [ ] Test Redis connection
  ```bash
  redis-cli ping
  ```
  Should return: `PONG`

- [ ] Check Redis info
  ```bash
  redis-cli info server
  ```
  Should show Redis version and uptime

## ✅ API Testing

- [ ] Visit Swagger UI: http://localhost:8000/docs

- [ ] Test Login endpoint
  - [ ] POST `/login`
  - [ ] Note: Will fail if no officers in database (expected)

- [ ] Create Test Officer (if admin access available)
  - [ ] POST `/officers`
  - [ ] Email: `test@example.com`
  - [ ] Password: `testpassword123`
  - [ ] Clearance level: `1`
  - [ ] Should return 201 Created

- [ ] Login with test officer
  - [ ] POST `/login`
  - [ ] Username: `test@example.com`
  - [ ] Password: `testpassword123`
  - [ ] Should return access token

- [ ] Get current officer
  - [ ] GET `/officers/me`
  - [ ] Add Authorization header with token
  - [ ] Should return officer details

- [ ] Create threat
  - [ ] POST `/threats`
  - [ ] Add Authorization header with token
  - [ ] Sample data:
    ```json
    {
      "content": "Test threat",
      "platform": "twitter",
      "threat_level": 3,
      "panic_score": 50
    }
    ```
  - [ ] Should return 201 Created

- [ ] List threats
  - [ ] GET `/threats`
  - [ ] Add Authorization header with token
  - [ ] Should return list of threats

## ✅ Docker Verification (Optional)

- [ ] Docker Desktop running
  ```bash
  docker ps
  ```
  Should not show connection error

- [ ] Start services with docker-compose
  ```bash
  docker-compose up -d
  ```

- [ ] Verify containers running
  ```bash
  docker ps
  ```
  Should show:
  - [ ] intel-postgres
  - [ ] intel-redis
  - [ ] intel-backend
  - [ ] intel-frontend

- [ ] Check logs
  ```bash
  docker-compose logs -f backend
  ```
  Should show "Application startup complete"

## ✅ Development Tools (Optional)

### VS Code Extensions
- [ ] Python extension installed
- [ ] REST Client extension installed
- [ ] SQLTools extension installed
- [ ] ES7+ React/Redux snippets installed

### Database GUI (Optional)
- [ ] pgAdmin installed and running (http://localhost:5050)
  OR
- [ ] DBeaver installed

### API Testing Tool (Optional)
- [ ] Thunder Client installed in VS Code
  OR
- [ ] Postman installed

## ✅ Common Tests

### Test WebSocket Connection (Advanced)
1. Get JWT token from login endpoint
2. Create `.rest` file with:
   ```
   @base = http://localhost:8000
   
   ### WebSocket Connection
   GET @base/ws/live-feed?token=YOUR_TOKEN_HERE
   ```
3. Use VS Code REST Client to test

### Test Real-time Updates
1. Create threat via API
2. Connect to WebSocket
3. Should receive threat update in real-time

## ✅ Troubleshooting Checklist

If something isn't working:

- [ ] Check all prerequisites are installed
- [ ] Verify virtual environment is activated
- [ ] Verify all services are running (PostgreSQL, Redis)
- [ ] Check `.env` file has all required variables
- [ ] Check for error messages in terminal
- [ ] Check browser console for JavaScript errors (F12)
- [ ] Check firewall isn't blocking ports
- [ ] Try restarting services
- [ ] Review [SETUP.md](SETUP.md) troubleshooting section
- [ ] Review [README.md](README.md#-troubleshooting) troubleshooting section
- [ ] Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common solutions

## 📝 Setup Verification Summary

Total checks: **70+**

Once all items are checked, your development environment is ready!

### Next Steps:
1. ✅ Review [README.md](README.md) for project overview
2. ✅ Review backend code in `backend/main.py`
3. ✅ Review frontend code in `frontend/src/App.jsx`
4. ✅ Start developing!

---

**Last Updated**: September 6, 2024

For help, check the documentation files:
- [README.md](README.md) - Project overview and API docs
- [SETUP.md](SETUP.md) - Detailed setup instructions
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick commands and examples
