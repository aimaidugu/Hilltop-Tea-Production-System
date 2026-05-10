# Railway Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Hilltop Tea Wage Tracking & Payroll System to Railway. Railway provides container-based deployment with managed PostgreSQL and excellent developer experience.

## Prerequisites

- Railway account (free tier available)
- GitHub account with project repository
- Basic familiarity with Git and command line
- Docker knowledge (optional but helpful)

## Preparation

### 1. Repository Setup

Ensure your repository contains all necessary files:
- Complete project structure
- `Procfile` for process management
- `railway.json` for Railway configuration
- `nixpacks.toml for build configuration
- `requirements.txt` with all dependencies

### 2. Railway Configuration Files

Verify the following configuration files:

**Procfile**:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app
```

**railway.json**:
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

**nixpacks.toml**:
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app"
```

## Deployment Steps

### Step 1: Create Railway Project

1. Log in to Railway at https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select the Hilltop Tea repository

### Step 2: Configure Build Settings

1. Railway will detect Python automatically
2. Verify build settings:
   - **Python Version**: 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app`

### Step 3: Add PostgreSQL Database

1. Click "New Service"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway will create and configure the database

### Step 4: Configure Environment Variables

1. Navigate to your web service
2. Click "Variables" tab
3. Add the following variables:

```
SECRET_KEY=your-generated-secret-key
DATABASE_URL=${{Postgres.DATABASE_URL}}
FLASK_ENV=production
PORT=${{PORT}}
```

4. Railway will automatically inject the PostgreSQL connection string

### Step 5: Initialize Database

1. Access the Railway console for your web service
2. Run the following commands:

```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial schema"

# Apply migration
flask db upgrade

# Seed admin user
flask shell
>>> from run import _seed_admin
>>> _seed_admin()
>>> exit()
```

### Step 6: Deploy

1. Railway will automatically deploy on push
2. Monitor deployment logs
3. Wait for deployment to complete
4. Access your application at the provided Railway URL

## Post-Deployment Configuration

### Domain Configuration

1. Navigate to your web service
2. Click "Settings" → "Domains"
3. Add custom domain if desired
4. Configure DNS records as instructed

### Database Access

1. Navigate to PostgreSQL service
2. Click "Connect" to view connection details
3. Use Railway's built-in query editor for database operations
4. Consider pgAdmin for advanced database management

### Monitoring Setup

1. Enable Railway metrics
2. Configure log retention
3. Set up alerting for critical errors
4. Monitor resource usage

## Railway-Specific Considerations

### Resource Limits

Free tier limitations:
- 512MB RAM per service
- 1 CPU core
- 1GB storage for database
- 500 hours of runtime per month

Consider upgrading when:
- Exceeding resource limits
- Need more storage
- Require better performance
- Need dedicated support

### Database Management

Railway PostgreSQL features:
- Automatic backups
- Point-in-time recovery
- Connection pooling
- Read replicas (paid tier)

### Health Checks

Configure health checks in `railway.json`:
```json
{
  "deploy": {
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "healthcheckInterval": 60
  }
}
```

### Logging

Railway provides:
- Real-time log streaming
- Log retention (7 days free, 30 days paid)
- Log search and filtering
- Integration with external log services

## Troubleshooting

### Build Failures

**Issue**: Build fails with dependency errors

**Solution**:
- Verify `requirements.txt` is complete
- Check Python version compatibility
- Review build logs for specific errors
- Try rebuilding with cache cleared

### Runtime Errors

**Issue**: Application returns 500 errors

**Solution**:
- Check environment variables are set correctly
- Verify database connection
- Review Railway logs
- Test database connectivity

### Database Connection Issues

**Issue**: Cannot connect to PostgreSQL

**Solution**:
- Verify DATABASE_URL is set correctly
- Check PostgreSQL service status
- Ensure services are in same project
- Test connection string locally

### Out of Memory Errors

**Issue**: Service crashes with OOM

**Solution**:
- Reduce worker count in Procfile
- Optimize memory usage
- Consider upgrading to paid tier
- Implement caching to reduce memory pressure

### Slow Performance

**Issue**: Application is slow to respond

**Solution**:
- Optimize database queries
- Add database indexes
- Increase worker count
- Consider upgrading resources

## Performance Optimization

### Database Optimization

- Add indexes to frequently queried columns
- Use connection pooling
- Optimize slow queries with EXPLAIN ANALYZE
- Consider read replicas for high traffic

### Application Optimization

- Use efficient query patterns
- Implement caching where appropriate
- Optimize worker configuration
- Monitor resource usage

### Scaling Strategy

- Start with free tier resources
- Monitor performance metrics
- Scale vertically (more resources)
- Scale horizontally (more instances) when needed

## Monitoring and Maintenance

### Railway Dashboard

Monitor the following:
- CPU and memory usage
- Request latency
- Error rates
- Database performance

### Log Management

- Review logs regularly
- Set up log alerts
- Archive important logs
- Consider external log aggregation

### Regular Maintenance

- Update dependencies regularly
- Review and optimize slow queries
- Monitor database size
- Apply security patches

## Backup and Recovery

### Database Backups

Railway provides:
- Automatic daily backups
- 7-day retention (free tier)
- Point-in-time recovery
- Manual backup options

### Backup Strategy

1. Enable automatic backups
2. Test restore process regularly
3. Export critical data periodically
4. Document recovery procedures

### Disaster Recovery

- Document recovery procedures
- Test restore process
- Maintain off-site backups
- Update recovery documentation

## Security Best Practices

### Environment Variables

- Never commit secrets to repository
- Use Railway's variable injection
- Rotate secrets regularly
- Monitor for leaked credentials

### Database Security

- Use strong database passwords
- Restrict database access
- Enable SSL connections
- Regular security updates

### Network Security

- Use HTTPS for all connections
- Configure firewall rules
- Monitor access logs
- Implement rate limiting

## Cost Management

### Free Tier Limits

- 512MB RAM per service
- 1GB storage
- 500 hours runtime
- 7-day log retention

### When to Upgrade

Consider upgrading when:
- Exceeding resource limits
- Need more storage
- Require better performance
- Need longer log retention

### Cost Optimization

- Optimize resource usage
- Use efficient queries
- Implement caching
- Monitor and reduce waste

## Support and Resources

### Railway Documentation

- Official docs: https://docs.railway.app
- Python guide: https://docs.railway.app/guides/deploy-python
- PostgreSQL: https://docs.railway.app/guides/postgresql

### Community Support

- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/railwayapp
- Stack Overflow: Tag with `railway`

### Additional Resources

- Railway templates: https://railway.app/templates
- Example projects: https://github.com/railwayapp
- Blog: https://blog.railway.app

This deployment guide ensures successful deployment of the Hilltop Tea system to Railway with proper configuration, monitoring, and maintenance procedures.
