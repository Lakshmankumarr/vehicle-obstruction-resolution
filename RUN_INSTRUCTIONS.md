# FreeWay Community - Complete Run Instructions

This document provides comprehensive instructions for running FreeWay Community in various environments.

## Table of Contents
1. [Quick Start (Windows)](#quick-start-windows)
2. [Quick Start (Linux/Mac)](#quick-start-linuxmac)
3. [Development Environment](#development-environment)
4. [Production Deployment (Docker)](#production-deployment-docker)
5. [Mobile App Development](#mobile-app-development)
6. [Testing](#testing)
7. [Environment Configuration](#environment-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start (Windows)

### Option 1: Interactive Launcher (Recommended)
```cmd
# Run the interactive backend launcher
run_backend.bat

# In a separate terminal, run the frontend launcher
run_frontend.bat
```

### Option 2: Docker Development (Easiest)
```cmd
# Start all services with Docker
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Quick Start (Linux/Mac)

### Option 1: Docker Development (Recommended)
```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Native Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (separate terminal)
cd FreewayApp
npm install
npx expo start --lan
```

---

## Development Environment

### Backend Requirements
- Python 3.11+
- PostgreSQL 14+ (or SQLite for zero-config)
- Redis 7+ (optional - has in-memory fallback)

### Frontend Requirements
- Node.js 18+
- npm 9+
- Expo CLI (`npm install -g expo-cli`)
- Android Studio (for Android) or Xcode (for iOS)

### Backend Setup (Native)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations (if using PostgreSQL)
alembic upgrade head

# Start development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Backend Setup (Docker)

```bash
# Development with hot reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# View logs
docker-compose -f docker-compose.yml -f docker-compose.override.yml logs -f backend

# Run migrations
docker-compose -f docker-compose.yml -f docker-compose.override.yml exec backend alembic upgrade head

# Access backend shell
docker-compose -f docker-compose.yml -f docker-compose.override.yml exec backend bash

# Stop
docker-compose -f docker-compose.yml -f docker-compose.override.yml down
```

### Frontend Setup

```bash
cd FreewayApp

# Install dependencies
npm install

# Start development server (LAN access for physical devices)
npx expo start --lan

# Start development server (localhost only)
npx expo start

# Start with cache reset
npx expo start --clear

# Run on Android (requires Android Studio/emulator)
npx expo run:android

# Run on iOS (requires macOS + Xcode)
npx expo run:ios
```

### Physical Device Testing

1. **Ensure phone and computer are on same Wi-Fi**
2. **Run backend with Docker or native** (must be accessible on LAN)
3. **Start Expo with LAN**: `npx expo start --lan`
4. **Scan QR code with Expo Go app** (Android) or Camera app (iOS)
5. **Backend URL**: The app uses `192.168.29.87:8000` by default. Change via:
   ```bash
   # Windows PowerShell
   $env:EXPO_PUBLIC_API_URL="http://YOUR_LAN_IP:8000"
   npx expo start --lan
   
   # Linux/Mac
   EXPO_PUBLIC_API_URL="http://YOUR_LAN_IP:8000" npx expo start --lan
   ```

---

## Production Deployment (Docker)

### Prerequisites
- Docker Desktop / Docker Engine + Docker Compose
- Domain name with DNS pointing to server
- Firebase project for push notifications
- (Optional) Plate Recognizer or OpenALPR API keys for real ALPR

### Step 1: Configure Environment

```bash
# Copy production template
cp .env.production .env

# Edit .env with YOUR values (REQUIRED!)
# Minimum required changes:
# - POSTGRES_PASSWORD=your_secure_password
# - SECRET_KEY=your_32_char_key (generate: openssl rand -base64 32)
# - ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Step 2: Add Firebase Credentials

```bash
# 1. Firebase Console > Project Settings > Service Accounts
# 2. Generate Private Key
# 3. Save as:
cp your-firebase-key.json backend/firebase-credentials.json
```

### Step 3: SSL Certificates

```bash
# Option A: Automatic Let's Encrypt (Recommended)
# Start nginx first (HTTP only for validation)
docker-compose up -d nginx

# Get certificate (replace yourdomain.com)
docker-compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email your-email@example.com \
  -d yourdomain.com \
  --agree-tos --no-eff-email

# Restart nginx to use HTTPS
docker-compose restart nginx

# Option B: Manual Certificates
# Place in certbot/conf/live/yourdomain.com/
# - fullchain.pem
# - privkey.pem
```

### Step 4: Deploy

```bash
# Build and start all services
docker-compose up --build -d

# Verify
docker-compose ps
# All services should show "Up" or "healthy"

# Check logs
docker-compose logs -f backend
```

### Production URLs
- **API**: https://yourdomain.com/api/v1
- **Docs**: https://yourdomain.com/docs (restrict in production!)
- **Health**: https://yourdomain.com/health
- **Ready**: https://yourdomain.com/ready

---

## Mobile App Development

### Development Workflow

```bash
cd FreewayApp

# 1. Install dependencies
npm install

# 2. Start Expo
npx expo start --lan

# 3. Test on device
# - Install Expo Go from App Store / Play Store
# - Scan QR code
# - App connects to your LAN backend
```

### Building for Production

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure project (first time)
eas build:configure

# Build Android AAB (for Play Store)
eas build --platform android --profile production

# Build iOS IPA (for App Store, macOS only)
eas build --platform ios --profile production

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

### Configuration Files

- **app.json**: App configuration (name, icons, permissions)
- **eas.json**: Build profiles and configuration
- **src/api/client.js**: API endpoint configuration
- **.env**: Frontend environment variables (if needed)

---

## Testing

### Backend Tests

```bash
# Native
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Docker
docker-compose -f docker-compose.yml -f docker-compose.override.yml exec backend pytest
```

### Frontend Tests

```bash
cd FreewayApp

# Run tests
npm test

# Watch mode
npm test -- --watch
```

### E2E Demo Script

```bash
# Start backend first (any method)
# Then run demo:
python demo_walkthrough.py
```

This runs a complete 9-step demonstration:
1. Health check
2. Register blocking vehicle owner (Priya)
3. Register obstructed driver (Rajesh)
4. Privacy-preserving plate lookup
5. Create obstruction request
6. Owner responds with ETA
7. Driver views live status
8. Mark resolved
9. History verification

---

## Environment Configuration

### Backend (.env) - Development

```env
# Application
DEBUG=true
LOG_LEVEL=DEBUG

# Database (SQLite for zero-config)
DATABASE_URL=sqlite:///./freeway.db

# Or PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost:5432/freeway_db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=dev-secret-key-min-32-chars-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Services (mock for development)
NOTIFICATION_PROVIDER=mock
ALPR_PROVIDER=mock

# Rate Limiting
RATE_LIMIT_HOURLY=30
RATE_LIMIT_DAILY=150
REQUEST_COOLDOWN_SECONDS=120

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8081","http://localhost:19006","*"]
```

### Backend (.env) - Production

```env
# Application
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://freeway:SECURE_PASSWORD@postgres:5432/freeway_community

# Redis
REDIS_URL=redis://redis:6379/0

# Security (GENERATE NEW KEYS!)
SECRET_KEY=your-generated-32-char-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Firebase (REQUIRED for push notifications)
NOTIFICATION_PROVIDER=firebase
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json

# ALPR (Choose one for real recognition)
ALPR_PROVIDER=plate_recognizer  # or openalpr
PLATE_RECOGNIZER_API_KEY=your-api-key
# OPENALPR_SECRET_KEY=your-secret-key
ALPR_COUNTRY=in

# Rate Limiting
RATE_LIMIT_HOURLY=30
RATE_LIMIT_DAILY=150
REQUEST_COOLDOWN_SECONDS=120

# CORS (RESTRICT TO YOUR DOMAINS!)
ALLOWED_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]
```

### Docker Compose Environment (.env)

```env
# Database
POSTGRES_DB=freeway_community
POSTGRES_USER=freeway
POSTGRES_PASSWORD=your_secure_password

# Backend uses these to construct DATABASE_URL and REDIS_URL
```

---

## Service Ports

| Service | Development | Production (Internal) | Production (External) |
|---------|-------------|----------------------|----------------------|
| Backend API | 8000 | 8000 | 80/443 (via Nginx) |
| PostgreSQL | 5432 | 5432 | Not exposed |
| Redis | 6379 | 6379 | Not exposed |
| Nginx | N/A | 80/443 | 80/443 |
| Expo Metro | 8081 | N/A | N/A |

---

## Common Commands

### Docker Compose

```bash
# Start development
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Start production
docker-compose up --build -d

# Stop
docker-compose down

# Stop + remove volumes (reset DB)
docker-compose down -v

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart backend

# Run command in container
docker-compose exec backend alembic upgrade head
docker-compose exec backend bash
docker-compose exec postgres psql -U freeway -d freeway_community
docker-compose exec redis redis-cli

# Scale backend (production)
docker-compose up --scale backend=3 -d
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1

# Current version
alembic current

# History
alembic history
```

### Backend Management

```bash
# Create superuser (if needed)
# python -c "from app.core.database import SessionLocal; from app.models.user import User; from app.utils.auth import hash_password; db=SessionLocal(); u=User(phoneNumber='+919999999999', name='Admin', passwordHash=hash_password('admin123'), isActive=True); db.add(u); db.commit()"

# Shell
python -c "from app.core.database import SessionLocal; from app.models import *; db=SessionLocal(); print('Ready')"
```

---

## Troubleshooting

### Backend Won't Start

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `Database connection failed` | Check PostgreSQL is running, verify DATABASE_URL |
| `Redis connection refused` | Start Redis or check REDIS_URL (falls back to in-memory) |
| `Address already in use` | Port 8000 in use: `lsof -i :8000` or change port |
| `Alembic: Target database not up to date` | Run `alembic upgrade head` |

### Frontend Issues

| Error | Solution |
|-------|----------|
| `Cannot connect to backend` | Use LAN IP, not localhost. Check firewall allows port 8000. |
| `Metro bundler errors` | `npx expo start --clear` |
| `Build fails` | `cd android && ./gradlew clean && cd ..` then rebuild |
| `iOS simulator issues` | `xcrun simctl erase all` then restart |

### Docker Issues

| Error | Solution |
|-------|----------|
| `Port already allocated` | Stop conflicting service: `docker stop $(docker ps -q)` |
| `Permission denied` | Linux: `sudo usermod -aG docker $USER` then relogin |
| `Out of disk space` | `docker system prune -a --volumes` |
| `PostgreSQL not ready` | Wait for healthcheck, increase `start_period` in compose |

### Database Issues

```bash
# Reset database completely (DEVELOPMENT ONLY)
docker-compose down -v
docker-compose up --build

# Or native
cd backend
rm freeway.db
alembic upgrade head
```

---

## Verification Checklist

### Development
- [ ] Backend responds at http://localhost:8000/health
- [ ] API docs at http://localhost:8000/docs
- [ ] Frontend loads in Expo Go
- [ ] Can register two users
- [ ] Can identify vehicle
- [ ] Can send/receive request
- [ ] Demo script passes: `python demo_walkthrough.py`

### Production
- [ ] HTTPS works: https://yourdomain.com/health
- [ ] API accessible: https://yourdomain.com/api/v1/health
- [ ] Database connected (check /ready)
- [ ] Redis connected (check /ready)
- [ ] Push notifications work (Firebase configured)
- [ ] ALPR works (API keys configured)
- [ ] CORS restricted to your domains
- [ ] Strong passwords/keys in .env
- [ ] Backups configured
- [ ] Monitoring/alerts set up

---

## Support

### Getting Help
1. Check logs: `docker-compose logs -f backend`
2. Verify health: `curl http://localhost:8000/ready`
3. Run demo: `python demo_walkthrough.py`
4. Check this guide's troubleshooting section

### Useful Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Expo Documentation](https://docs.expo.dev/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

---

## File Structure Reference

```
Vehicle-Obstruction-resolution/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # API routes
│   │   ├── core/              # Config, DB, Redis
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities
│   ├── alembic/               # Migrations
│   ├── tests/                 # Backend tests
│   ├── main.py                # Entry point
│   ├── requirements.txt       # Python deps
│   ├── Dockerfile             # Docker image
│   └── .env.example           # Env template
├── FreewayApp/                # React Native Frontend
│   ├── src/
│   │   ├── api/               # API client
│   │   ├── components/        # Reusable UI
│   │   ├── context/           # React context
│   │   ├── navigation/        # Navigation
│   │   ├── screens/           # App screens
│   │   └── theme/             # Design tokens
│   ├── app.json               # Expo config
│   ├── package.json           # Node deps
│   └── babel.config.js        # Babel config
├── nginx/                     # Nginx config
│   ├── nginx.conf
│   └── conf.d/default.conf
├── certbot/                   # SSL certificates
├── docker-compose.yml         # Production compose
├── docker-compose.override.yml # Development compose
├── .env.production            # Production env template
├── run_backend.bat            # Windows backend launcher
├── run_frontend.bat           # Windows frontend launcher
├── demo_walkthrough.py        # E2E demo script
├── DOCKER_DEPLOYMENT.md       # Detailed Docker guide
├── RUN_INSTRUCTIONS.md        # This file
└── PROJECT_ANALYSIS.md        # Project status analysis
```

---

*Generated with [Claude Code](https://claude.com/claude-code)*