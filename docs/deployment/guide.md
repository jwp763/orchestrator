# Deployment Guide

*Last Updated: 2025-01-11*

## Overview

This guide covers deploying the Databricks Orchestrator to various environments, from local development to production cloud infrastructure.

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+ (production)
- Redis 6+ (optional, for caching)
- Docker 20+ (for containerized deployment)

### Required Tools
```bash
# Install deployment tools
pip install ansible fabric
npm install -g pm2
```

## Environment Configuration

### Environment Variables

Create `.env` files for each environment:

```bash
# .env.development
DATABASE_URL=sqlite:///./dev.db
AI_PROVIDER=openai
AI_API_KEY=sk-dev-...
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=DEBUG

# .env.production
DATABASE_URL=postgresql://user:pass@host:5432/orchestrator
AI_PROVIDER=anthropic
AI_API_KEY=sk-prod-...
CORS_ORIGINS=https://orchestrator.example.com
LOG_LEVEL=INFO
SECRET_KEY=generate-strong-secret-key
```

### Configuration Files

```yaml
# config/production.yaml
database:
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30

redis:
  host: redis.example.com
  port: 6379
  db: 0

ai:
  timeout: 30
  max_retries: 3
  
security:
  jwt_expiry: 3600
  refresh_token_expiry: 604800
```

## Local Development

### Quick Start
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/orchestrator
    depends_on:
      - db
      
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://backend:8000
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=orchestrator
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Production Deployment

### 1. Database Setup

#### PostgreSQL Configuration
```sql
-- Create production database
CREATE DATABASE orchestrator;
CREATE USER orchestrator_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE orchestrator TO orchestrator_user;

-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

#### Run Migrations
```bash
export DATABASE_URL=postgresql://user:pass@host:5432/orchestrator
alembic upgrade head
```

### 2. Backend Deployment

#### Using Gunicorn
```bash
# Install production dependencies
pip install gunicorn uvloop httptools

# Run with Gunicorn
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --preload
```

#### Systemd Service
```ini
# /etc/systemd/system/orchestrator-backend.service
[Unit]
Description=Orchestrator Backend API
After=network.target

[Service]
Type=notify
User=orchestrator
Group=orchestrator
WorkingDirectory=/opt/orchestrator/backend
Environment="PATH=/opt/orchestrator/venv/bin"
ExecStart=/opt/orchestrator/venv/bin/gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind unix:/tmp/orchestrator.sock \
  --log-level info
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Frontend Deployment

#### Build for Production
```bash
cd frontend
npm run build

# Output in dist/ directory
```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/orchestrator
server {
    listen 80;
    server_name orchestrator.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name orchestrator.example.com;
    
    ssl_certificate /etc/ssl/certs/orchestrator.crt;
    ssl_certificate_key /etc/ssl/private/orchestrator.key;
    
    # Frontend
    location / {
        root /opt/orchestrator/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API proxy
    location /api {
        proxy_pass http://unix:/tmp/orchestrator.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running AI requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://unix:/tmp/orchestrator.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. Process Management

#### PM2 Configuration
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'orchestrator-backend',
    script: 'gunicorn',
    args: 'src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000',
    cwd: '/opt/orchestrator/backend',
    env: {
      NODE_ENV: 'production',
      DATABASE_URL: process.env.DATABASE_URL
    },
    error_file: '/var/log/orchestrator/error.log',
    out_file: '/var/log/orchestrator/out.log',
    log_file: '/var/log/orchestrator/combined.log',
    time: true
  }]
};
```

## Cloud Deployments

### AWS Deployment

#### Using Elastic Beanstalk
```yaml
# .elasticbeanstalk/config.yml
branch-defaults:
  main:
    environment: orchestrator-prod
    
global:
  application_name: orchestrator
  default_platform: Python 3.9
  default_region: us-east-1
  
option_settings:
  aws:elasticbeanstalk:application:environment:
    DATABASE_URL: "postgresql://..."
    AI_API_KEY: "sk-..."
```

#### Using ECS
```json
// task-definition.json
{
  "family": "orchestrator",
  "taskRoleArn": "arn:aws:iam::123456789012:role/orchestratorTask",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/orchestrator:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:orchestrator/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/orchestrator",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Using App Engine
```yaml
# app.yaml
runtime: python39

env_variables:
  DATABASE_URL: "postgresql://..."

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 2
  max_instances: 10

handlers:
- url: /api/.*
  script: auto
  secure: always
  
- url: /.*
  static_files: frontend/dist/index.html
  upload: frontend/dist/index.html
  secure: always
```

#### Using Cloud Run
```dockerfile
# Dockerfile.cloudrun
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 src.main:app
```

### Kubernetes Deployment

#### Deployment Manifest
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orchestrator-backend
  template:
    metadata:
      labels:
        app: orchestrator-backend
    spec:
      containers:
      - name: backend
        image: orchestrator/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: orchestrator-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service & Ingress
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: orchestrator-backend
spec:
  selector:
    app: orchestrator-backend
  ports:
  - port: 80
    targetPort: 8000

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orchestrator-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - orchestrator.example.com
    secretName: orchestrator-tls
  rules:
  - host: orchestrator.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: orchestrator-backend
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: orchestrator-frontend
            port:
              number: 80
```

## Monitoring & Logging

### Application Monitoring

#### Prometheus Metrics
```python
# src/monitoring.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_count = Counter(
    'orchestrator_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'orchestrator_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

active_projects = Gauge(
    'orchestrator_active_projects',
    'Number of active projects'
)
```

#### Health Checks
```python
# src/health.py
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "ai_provider": await check_ai_provider()
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    status_code = 200 if status == "healthy" else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Logging Configuration

#### Structured Logging
```python
# src/logging_config.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.render_to_log_kwargs,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

#### Log Aggregation
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/orchestrator/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "orchestrator-%{+yyyy.MM.dd}"
```

## Security Hardening

### SSL/TLS Configuration
```bash
# Generate certificates with Let's Encrypt
certbot --nginx -d orchestrator.example.com

# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

### Security Headers
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

### API Rate Limiting
```python
# src/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/planner/generate")
@limiter.limit("10/minute")
async def generate_plan(request: Request):
    # Implementation
```

## Backup & Recovery

### Database Backups
```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# PostgreSQL backup
pg_dump $DATABASE_URL > $BACKUP_DIR/orchestrator_$TIMESTAMP.sql

# Compress and encrypt
gzip $BACKUP_DIR/orchestrator_$TIMESTAMP.sql
gpg --encrypt --recipient backup@example.com $BACKUP_DIR/orchestrator_$TIMESTAMP.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/orchestrator_$TIMESTAMP.sql.gz.gpg s3://orchestrator-backups/

# Cleanup old backups
find $BACKUP_DIR -name "*.sql.gz.gpg" -mtime +7 -delete
```

### Disaster Recovery
```yaml
# disaster-recovery.yaml
recovery_objectives:
  rto: 4 hours  # Recovery Time Objective
  rpo: 1 hour   # Recovery Point Objective

backup_strategy:
  database:
    frequency: hourly
    retention: 7 days
    location: 
      - primary: s3://orchestrator-backups
      - secondary: glacier://orchestrator-archives
  
  files:
    frequency: daily
    retention: 30 days
    
failover_procedure:
  - promote_read_replica
  - update_dns_records
  - verify_application_health
  - notify_stakeholders
```

## Deployment Checklist

### Pre-deployment
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates valid
- [ ] Backup strategy in place

### Deployment Steps
- [ ] Create database backup
- [ ] Deploy backend changes
- [ ] Run database migrations
- [ ] Deploy frontend changes
- [ ] Clear caches
- [ ] Verify health checks
- [ ] Update documentation

### Post-deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify AI integrations
- [ ] Test critical paths
- [ ] Update status page
- [ ] Notify team

## Rollback Procedures

### Quick Rollback
```bash
# Backend rollback
kubectl rollout undo deployment/orchestrator-backend

# Database rollback
alembic downgrade -1

# Frontend rollback
aws s3 sync s3://orchestrator-frontend-previous/ s3://orchestrator-frontend-current/ --delete
```

### Full Rollback Plan
1. Stop incoming traffic
2. Restore database from backup
3. Deploy previous backend version
4. Deploy previous frontend version
5. Clear all caches
6. Verify system health
7. Resume traffic
8. Incident post-mortem

## Related Documentation

- [Infrastructure as Code](../infrastructure/terraform.md)
- [CI/CD Pipeline](../ci-cd/pipeline.md)
- [Monitoring Guide](../monitoring/guide.md)
- [Security Best Practices](../security/best-practices.md)