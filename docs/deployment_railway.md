# HILLTOP TEA — Railway Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying Hilltop Tea to Railway. Railway is a container-based platform that provides PostgreSQL databases and application hosting with excellent developer experience.

## Prerequisites

- Railway account (free tier is sufficient)
- GitHub repository with the Hilltop Tea code
- Git installed locally

## Step 1: Prepare Your Repository

Ensure your repository includes all necessary files:

- `run.py` - Application entry point
- `requirements.txt` - Python dependencies
- `Procfile` - Process configuration
- `railway.json` - Railway configuration
- `nixpacks.toml` - Build configuration
- `.env.example` - Environment variable template

## Step 2: Create a Railway Project

1. Log in to Railway at railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select your Hilltop Tea repository

## Step 3: Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway will provision a PostgreSQL database

## Step 4: Configure Environment Variables

1. Click on your application service
2. Go to the "Variables" tab
3. Add the following variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate with `openssl rand -hex 32` |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | Railway will automatically set this from the PostgreSQL service |
| `PORT` | Railway will automatically set this |

## Step 5: Configure Build Settings

Railway will automatically detect Python and use the `nixpacks.toml` configuration. Verify the following:

**nixpacks.toml:**
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app"
```

**railway.json:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app",
    "healthcheckPath": "/"
  }
}
```

**Procfile:**
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app
```

## Step 6: Deploy

1. Railway will automatically deploy on push to GitHub
2. Monitor the deployment logs in the Railway dashboard
3. Wait for the deployment to complete successfully

## Step 7: Run Database Migrations

After first deployment, initialize the database schema:

1. Click on your application service
2. Go to the "Console" tab
3. Open a new terminal
4. Run the following commands:

```bash
flask db upgrade
```

5. Seed the admin account:

```bash
flask shell -c "from run import _seed_admin; _seed_admin()"
```

## Step 8: Verify Deployment

1. Click on your application service
2. Copy the domain URL from the dashboard
3. Visit the URL in your browser
4. Log in with the default credentials (admin / admin123)
5. Change the default password immediately
6. Test key functionality

## Configuration Details

### Procfile

The Procfile tells Railway how to start your application:

```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app
```

- `web`: Indicates this is a web service
- `gunicorn`: The WSGI server
- `--bind 0.0.0.0:$PORT`: Binds to all interfaces on the Railway-provided port
- `--workers 2`: Uses 2 worker processes
- `--timeout 60`: Sets request timeout to 60 seconds
- `run:app`: Imports the app from run.py

### nixpacks.toml

Nixpacks handles the build environment:

```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app"
```

- `python311`: Ensures Python 3.11 is used
- `postgresql`: Includes PostgreSQL libraries for psycopg2-binary

### railway.json

Railway-specific configuration:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app",
    "healthcheckPath": "/"
  }
}
```

- `builder`: Specifies Nixpacks as the build system
- `startCommand`: Overrides the default start command
- `healthcheckPath`: Path for health checks

## Troubleshooting

### Issue: Build fails with psycopg2 compilation error

**Solution:** Ensure `postgresql` is included in `nixPkgs` in `nixpacks.toml`. This provides the necessary PostgreSQL libraries.

### Issue: Application fails to start

**Solution:** Check the deployment logs in the Railway dashboard. Verify the `PORT` environment variable is set correctly. Ensure the `run:app` import works correctly.

### Issue: Database connection errors

**Solution:** Verify the PostgreSQL service is running. Check that the `DATABASE_URL` is correctly set by Railway. Ensure the database migrations have been run.

### Issue: Health check failures

**Solution:** Verify the health check path is accessible. Check that the application responds to GET requests on `/`. Review the application logs for errors.

## Performance Optimization

### Worker Configuration

Adjust the number of workers based on your needs:

```bash
# For more CPU cores
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 60 run:app

# For memory-constrained environments
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 60 run:app
```

### Database Connection Pooling

SQLAlchemy automatically manages connection pooling. For high-traffic scenarios, consider tuning the pool size:

```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
}
```

### Caching

Consider implementing caching for frequently accessed data:

```python
# Install redis
pip install redis

# Configure Redis cache
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
```

## Security Considerations

1. **HTTPS:** Railway automatically provisions SSL certificates
2. **Secret Management:** Use Railway's environment variables for secrets
3. **Database Security:** Railway PostgreSQL is isolated and secure
4. **Rate Limiting:** Consider implementing rate limiting for API endpoints

## Scaling

Railway automatically scales based on resource usage. For production:

1. **Upgrade Plan:** Consider the Pro plan for higher limits
2. **Horizontal Scaling:** Add more worker processes
3. **Database Scaling:** Upgrade PostgreSQL instance for higher performance
4. **Monitoring:** Use Railway's metrics to monitor performance

## Cost Considerations

Railway's free tier includes:
- $5 credit per month
- 512MB RAM per service
- Shared CPU

For production use, consider the Pro plan ($20/month) for:
- 1GB RAM per service
- Dedicated CPU
- Priority support
- Higher limits

## Backup and Recovery

### Database Backups

Railway automatically creates daily backups. To restore:

1. Go to your PostgreSQL service
2. Click on the "Backups" tab
3. Select a backup to restore

### Manual Backup

```bash
# From Railway console
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

## Monitoring

### Application Logs

View logs in the Railway dashboard under the "Logs" tab for your application service.

### Database Metrics

Monitor PostgreSQL performance in the database service dashboard.

### Health Checks

Railway performs health checks on the configured path. Monitor these in the application service dashboard.
