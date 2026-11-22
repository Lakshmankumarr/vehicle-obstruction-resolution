# FreeWay Community - Docker Deployment Guide

This guide covers deploying FreeWay Community using Docker Compose for both development and production environments.

## Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine + Docker Compose** (Linux)
- **Domain name** (for production SSL)
- **Firebase project** (for push notifications in production)

---

## Quick Start (Development)

```bash
# Clone and navigate
cd Vehicle-Obstruction-resolution

# Start development environment (no SSL, mock services)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Services available at:
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Development Features
- Hot reload enabled for backend code changes
- Mock ALPR and notification providers
- SQLite fallback if PostgreSQL unavailable
- Debug logging enabled

---

## Production Deployment

### 1. Prepare Environment

```bash
# Copy production environment template
cp .env.production .env

# Edit .env with your actual values (REQUIRED!)
# - POSTGRES_PASSWORD: Secure database password
# - SECRET_KEY: Generate with: openssl rand -base64 32
# - FIREBASE_CREDENTIALS_PATH: /app/firebase-credentials.json
# - PLATE_RECOGNIZER_API_KEY or OPENALPR_SECRET_KEY (for real ALPR)
# - ALLOWED_ORIGINS: Your actual domain(s)
```

### 2. Add Firebase Credentials (Required for Push Notifications)

```bash
# 1. Go to Firebase Console > Project Settings > Service Accounts
# 2. Generate new private key
# 3. Save as backend/firebase-credentials.json
cp path/to/your/firebase-credentials.json backend/firebase-credentials.json
```

### 3. SSL Certificates (Let's Encrypt)

For production HTTPS, you have two options:

#### Option A: Automatic (Certbot) - Recommended
```bash
# 1. Ensure your domain points to this server
# 2. Start with HTTP first to validate domain
docker-compose up -d nginx

# 3. Get certificate (replace yourdomain.com)
docker-compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email your-email@example.com \
  -d yourdomain.com \
  --agree-tos --no-eff-email

# 4. Restart nginx to use certificates
docker-compose restart nginx
```

#### Option B: Manual Certificates
```bash
# Place your certificates in:
mkdir -p certbot/conf/live/yourdomain.com/
# certbot/conf/live/yourdomain.com/fullchain.pem
# certbot/conf/live/yourdomain.com/privkey.pem
```

### 4. Deploy Production Stack

```bash
# Build and start all services
docker-compose up --build -d

# Verify services are healthy
docker-compose ps

# Check logs
docker-compose logs -f backend
```

---

## Service Architecture

```
┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│   Backend   │
│  (Port 80/  │     │  (Port 8000)│
│   443)      │     └──────┬──────┘
└─────────────┘            │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  PostgreSQL │     │    Redis    │
                    │  (Port 5432)│     │  (Port 6379)│
                    └─────────────┘     └─────────────┘
```

---

## Configuration Reference

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | Yes | - | Redis connection string |
| `SECRET_KEY` | Yes | - | JWT signing key (32+ chars) |
| `ALGORITHM` | No | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | 60 | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | 30 | Refresh token lifetime |
| `NOTIFICATION_PROVIDER` | No | mock | mock/console/firebase |
| `FIREBASE_CREDENTIALS_PATH` | If firebase | - | Path to Firebase service account |
| `ALPR_PROVIDER` | No | mock | mock/plate_recognizer/openalpr |
| `PLATE_RECOGNIZER_API_KEY` | If plate_recognizer | - | API key from platerecognizer.com |
| `OPENALPR_SECRET_KEY` | If openalpr | - | Secret key from openalpr.com |
| `ALPR_COUNTRY` | No | in | Country code for ALPR |
| `RATE_LIMIT_HOURLY` | No | 30 | Requests per hour |
| `RATE_LIMIT_DAILY` | No | 150 | Requests per day |
| `REQUEST_COOLDOWN_SECONDS` | No | 120 | Cooldown between same vehicle |
| `REQUEST_EXPIRY_MINUTES` | No | 30 | Request expiration time |
| `STRIKE_THRESHOLD` | No | 3 | Reports before auto-flag |
| `DATA_RETENTION_DAYS` | No | 90 | Audit log retention |
| `ALLOWED_ORIGINS` | Yes | - | CORS allowed origins (JSON array) |
| `LOG_LEVEL` | No | INFO | Logging level |

### Database Connection

```bash
# Inside backend container
DATABASE_URL=postgresql://freeway:PASSWORD@postgres:5432/freeway_community

# From host (for migrations)
DATABASE_URL=postgresql://freeway:PASSWORD@localhost:5432/freeway_community
```

---

## Running Migrations

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.override.yml exec backend alembic upgrade head

# Production
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

---

## Health Checks & Monitoring

```bash
# Liveness probe (for Kubernetes/load balancer)
curl http://localhost:8000/health
# Returns: {"status": "ok"}

# Readiness probe (checks DB + Redis)
curl http://localhost:8000/ready
# Returns: {"status": "ready", "database": "connected", "redis": "connected"}

# Service health
docker-compose ps
# All services should show "healthy" or "Up"
```

---

## Logs & Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 backend

# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec postgres psql -U freeway -d freeway_community

# Access Redis
docker-compose exec redis redis-cli
```

---

## Backup & Restore

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U freeway freeway_community > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker-compose exec postgres pg_dump -U freeway freeway_community | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Database Restore
```bash
# From SQL file
docker-compose exec -T postgres psql -U freeway -d freeway_community < backup_20261122_120000.sql

# From compressed
gunzip -c backup_20261122_120000.sql.gz | docker-compose exec -T postgres psql -U freeway -d freeway_community
```

### Volume Backup (Complete)
```bash
# Stop services
docker-compose down

# Backup volumes
docker run --rm -v freeway_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
docker run --rm -v freeway_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v freeway_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

---

## Scaling Considerations

### Horizontal Scaling (Multiple Backend Instances)
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # ... rest of config
```
Then use Nginx upstream with multiple backend servers.

### Database Scaling
- **Read replicas**: Add replica PostgreSQL instances
- **Connection pooling**: Use PgBouncer (already configured in settings)

### Redis Scaling
- **Redis Cluster**: For high availability
- **Sentinel**: For automatic failover

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Backend fails to start | Check `docker-compose logs backend` - usually DB connection or missing env vars |
| PostgreSQL not ready | Wait for healthcheck, or increase `start_period` |
| Redis connection refused | Verify Redis service is healthy, check REDIS_URL |
| SSL certificate errors | Ensure certbot volume mounted, domain points to server |
| CORS errors | Update ALLOWED_ORIGINS in .env, restart backend |
| Push notifications not working | Verify FIREBASE_CREDENTIALS_PATH and NOTIFICATION_PROVIDER=firebase |
| ALPR always returns mock | Set ALPR_PROVIDER and add API keys |

### Reset Everything (Development)
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml down -v
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

---

## Security Checklist (Production)

- [ ] Strong `POSTGRES_PASSWORD` (32+ chars)
- [ ] Strong `SECRET_KEY` (generated with `openssl rand -base64 32`)
- [ ] `NOTIFICATION_PROVIDER=firebase` with valid credentials
- [ ] Real ALPR provider configured (`plate_recognizer` or `openalpr`)
- [ ] `ALLOWED_ORIGINS` restricted to your domains only
- [ ] SSL certificates valid and auto-renewing
- [ ] Firewall: Only ports 80, 443 exposed publicly
- [ ] Database not exposed to internet
- [ ] Redis not exposed to internet
- [ ] Regular backups scheduled
- [ ] Log monitoring configured
- [ ] Alerting for error rates > 5%

---

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up --build -d

# Run migrations if needed
docker-compose exec backend alembic upgrade head
```

---

## Support

For issues:
1. Check logs: `docker-compose logs -f backend`
2. Verify health: `curl http://localhost:8000/ready`
3. Check service status: `docker-compose ps`
4. Review this guide for common issues