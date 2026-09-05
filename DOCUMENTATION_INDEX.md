# Documentation Index

Welcome to the Intelligence Dashboard project! This guide explains all the documentation available in this repository.

## 📚 Main Documentation

### [README.md](README.md)
**The main project documentation**

Contains:
- Project overview and features
- Technology stack details
- Quick start guide with Docker
- Full API documentation
- All endpoints with examples
- Security and authorization info
- Troubleshooting guide
- Environment variables reference
- Deployment instructions

**Start here if you want:** Overview of the entire project

---

### [SETUP.md](SETUP.md)
**Complete setup guide for all platforms**

Contains:
- Quick start with Docker
- Prerequisites for different platforms
- Step-by-step backend setup
- Step-by-step frontend setup
- PostgreSQL installation options (Installer, WSL2, Docker, Package Managers)
- Redis installation options (Docker, WSL2, Memurai, Binary)
- Environment configuration
- Detailed verification steps
- Platform-specific troubleshooting
- Windows Terminal tips
- VS Code extensions recommendations
- Database and API testing tools

**Start here if you want:** Detailed setup instructions for your platform

---

### [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
**Quick commands and code snippets**

Contains:
- Quick start commands
- Common API examples (curl and code)
- Quick fixes for common issues
- Docker commands reference
- Database operations
- Environment variables summary
- Useful URLs
- Development workflow tips
- Keyboard shortcuts
- Quick links to resources

**Start here if you want:** Fast lookup of commands and code examples

---

### [SETUP_VERIFICATION.md](SETUP_VERIFICATION.md)
**Verification checklist for setup**

Contains:
- Prerequisites checklist
- Project structure verification
- Backend setup checklist
- Frontend setup checklist
- Verification procedures
- API testing steps
- Docker verification (optional)
- Development tools (optional)
- Common tests
- Troubleshooting checklist
- Summary with next steps

**Start here if you want:** Verify your setup is working correctly

---

## 🎯 Choose Your Starting Point

### I want to understand what this project does
→ Start with [README.md](README.md) - Project Overview section

### I want to get the project running quickly
→ Start with [SETUP.md](SETUP.md) - Quick Start (Docker) section

### I already have it set up and want to start developing
→ Start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### I'm troubleshooting an issue
→ Check the Troubleshooting section in [SETUP.md](SETUP.md) or [README.md](README.md)

### I need to verify my setup works
→ Use [SETUP_VERIFICATION.md](SETUP_VERIFICATION.md)

### I want to deploy to production
→ See [README.md](README.md) - Deployment section

---

## 🔗 File Structure

```
osnit-project/
├── README.md                      # Main project documentation
├── SETUP.md                       # Setup instructions for all platforms
├── QUICK_REFERENCE.md            # Quick commands and examples
├── SETUP_VERIFICATION.md         # Verification checklist
├── DOCUMENTATION_INDEX.md         # This file
├── docker-compose.yml            # Docker Compose configuration
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore patterns
│
├── backend/
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Backend configuration (git ignored)
│   ├── .env.example              # Example backend configuration
│   ├── .dockerignore             # Docker ignore patterns
│   ├── Dockerfile                # Docker image for backend
│   ├── main.py                   # FastAPI application
│   ├── models.py                 # Database models
│   ├── schemas.py                # Pydantic schemas
│   ├── database.py               # Database configuration
│   ├── auth.py                   # Authentication logic
│   ├── crud.py                   # Database operations
│   └── stream_processor.py       # Kafka consumer
│
└── frontend/
    ├── package.json              # Node dependencies
    ├── .env                      # Frontend configuration (git ignored)
    ├── .dockerignore             # Docker ignore patterns
    ├── Dockerfile                # Docker image for frontend
    ├── vite.config.js            # Vite configuration
    ├── index.html                # HTML entry point
    ├── README.md                 # Frontend-specific docs
    └── src/
        ├── main.jsx              # React entry point
        ├── App.jsx               # Main App component
        ├── AuthContext.jsx       # Auth context provider
        ├── Login.jsx             # Login page
        ├── Dashboard.jsx         # Main dashboard
        └── assets/               # Static assets
```

---

## ⚡ Quick Links by Task

### Installation & Setup
- [Quick Docker setup](SETUP.md#quick-start-docker)
- [Manual backend setup](SETUP.md#backend-setup)
- [Manual frontend setup](SETUP.md#frontend-setup)
- [Windows-specific setup](SETUP.md#quick-start-windows)

### Database & Infrastructure
- [PostgreSQL setup](SETUP.md#database-setup)
- [Redis setup](SETUP.md#cache-setup)
- [Docker Compose](docker-compose.yml)

### API Reference
- [All endpoints](README.md#-api-documentation)
- [Authentication](README.md#-security--authorization)
- [WebSocket connection](README.md#websocket-live-feed)
- [Example requests](QUICK_REFERENCE.md#api-quick-examples)

### Troubleshooting
- [Database errors](SETUP.md#postgresql-connection-errors)
- [Redis errors](SETUP.md#redis-connection-errors)
- [Port conflicts](SETUP.md#port-conflicts)
- [Dependencies issues](SETUP.md#dependencies-not-found)
- [Docker issues](SETUP.md#docker-issues)

### Development
- [Development workflow](SETUP.md#development-workflow)
- [VS Code setup](SETUP.md#vs-code-extensions-recommended)
- [API testing](SETUP.md#api-testing)
- [Database management](SETUP.md#database-management)

### Deployment
- [Docker deployment](README.md#quick-deployment-with-docker-compose-recommended)
- [Production setup](README.md#production-deployment)

---

## 📞 Common Questions

### Q: Where do I start?
**A:** If you're setting up for the first time, go to [SETUP.md](SETUP.md)

### Q: How do I run the project?
**A:** Use Docker: `docker-compose up -d` or see [SETUP.md](SETUP.md) for manual setup

### Q: Where are the API docs?
**A:** Run the backend and visit http://localhost:8000/docs

### Q: How do I create users?
**A:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#api-quick-examples) for API examples

### Q: What if something doesn't work?
**A:** Check [SETUP.md - Troubleshooting](SETUP.md#troubleshooting) first

### Q: How do I deploy to production?
**A:** See [README.md - Deployment](README.md#-deployment)

### Q: Where are the code examples?
**A:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### Q: How do I verify setup is correct?
**A:** Use [SETUP_VERIFICATION.md](SETUP_VERIFICATION.md)

---

## 🚀 Quick Start Paths

### Path 1: Docker (Recommended - 5 minutes)
1. Install Docker Desktop
2. Run: `docker-compose up -d`
3. Visit http://localhost:8000/docs

### Path 2: Manual Setup (20 minutes)
1. Follow [SETUP.md](SETUP.md)
2. Start backend: `uvicorn main:app --reload`
3. Start frontend: `npm run dev`
4. Visit http://localhost:8000/docs

### Path 3: Development Environment
1. Complete Path 1 or 2
2. Install VS Code extensions from [SETUP.md](SETUP.md)
3. Start developing!

---

## 📖 Environment Files

### `.env` files (not in git)
Located in `backend/.env` and created from examples

Contains sensitive configuration:
- Database credentials
- JWT secrets
- API URLs

### `.env.example` files (in git)
Template for configuration

Safe to store in git - contains no secrets

---

## 🔐 Security Notes

### Development
- ✅ Use example credentials for development
- ✅ Store real credentials in `.env` (git ignored)
- ✅ Review security settings before production

### Production
- ❌ Never commit `.env` files
- ❌ Never hardcode secrets
- ✅ Use environment variables or secrets manager
- ✅ Change default passwords
- ✅ Enable HTTPS/SSL
- ✅ Set strong JWT_SECRET_KEY

---

## 📝 File Descriptions

| File | Purpose |
|------|---------|
| README.md | Main project documentation |
| SETUP.md | Detailed setup guide |
| QUICK_REFERENCE.md | Quick commands and examples |
| SETUP_VERIFICATION.md | Setup verification checklist |
| docker-compose.yml | Multi-container Docker setup |
| .env.example | Environment variables template |
| requirements.txt | Python dependencies |
| package.json | Node dependencies |

---

## 🎓 Learning Path

**New to this project?**
1. Read [README.md](README.md) - Project overview (5 min)
2. Follow [SETUP.md](SETUP.md) - Get it running (15-30 min)
3. Use [SETUP_VERIFICATION.md](SETUP_VERIFICATION.md) - Verify setup (5 min)
4. Explore [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Test API (10 min)
5. Start coding! (Read [README.md](README.md#-api-documentation) for API details)

**Familiar with the project?**
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
2. Visit http://localhost:8000/docs for API details
3. Review code in `backend/main.py` and `frontend/src/`

---

## 🔄 Documentation Updates

This documentation is updated with the project. 

Last Updated: September 6, 2024

If you find issues or have suggestions, please update the relevant documentation file.

---

## 📞 Getting Help

1. **Check Documentation**: Review the relevant file above
2. **Search Troubleshooting**: See [SETUP.md](SETUP.md#troubleshooting)
3. **Test Setup**: Use [SETUP_VERIFICATION.md](SETUP_VERIFICATION.md)
4. **API Docs**: Visit http://localhost:8000/docs
5. **Code Review**: Check the relevant source file

---

**Start here:** [README.md](README.md) for overview, [SETUP.md](SETUP.md) for setup, [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for quick commands
