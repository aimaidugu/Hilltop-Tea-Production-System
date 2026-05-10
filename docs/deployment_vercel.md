# Vercel Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Hilltop Tea Wage Tracking & Payroll System to Vercel. Vercel provides serverless hosting with excellent static file serving and global CDN capabilities.

## Prerequisites

- Vercel account (free tier available)
- GitHub account with project repository
- Supabase account for PostgreSQL database (recommended)
- Basic familiarity with Git and command line

## Preparation

### 1. Repository Setup

Ensure your repository contains all necessary files:
- Complete project structure
- `api/index.py` as Vercel entry point
- `vercel.json` configuration
- `requirements.txt` with all dependencies
- `.env.example` for environment variables

### 2. Database Setup

For production deployment, use Supabase PostgreSQL:

1. Create a Supabase project at https://supabase.com
2. Navigate to Settings → Database
3. Copy the connection string
4. Format as: `postgresql://user:password@host:port/database`

### 3. Environment Variables

Prepare the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | Flask session secret | Generate with `openssl rand -hex 32` |
| DATABASE_URL | PostgreSQL connection | `postgresql://user:pass@host/db` |
| FLASK_ENV | Environment | `production` |

## Deployment Steps

### Step 1: Connect to Vercel

1. Log in to Vercel at https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Select the repository containing the Hilltop Tea project

### Step 2: Configure Project

1. **Framework Preset**: Select "Other"
2. **Root Directory**: Leave as default (root of repository)
3. **Build Command**: Leave blank (Vercel handles Python builds)
4. **Output Directory**: Leave blank

### Step 3: Set Environment Variables

1. Navigate to Settings → Environment Variables
2. Add the following variables:

```
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
FLASK_ENV=production
```

3. Select all environments (Development, Preview, Production)

### Step 4: Deploy

1. Click "Deploy"
2. Vercel will build and deploy your application
3. Wait for deployment to complete (typically 2-3 minutes)
4. Access your application at the provided URL

## Post-Deployment Configuration

### Database Initialization

After deployment, initialize the database:

1. Access your application URL
2. The default admin account will be created automatically
3. Log in with: `admin / admin123`
4. Change the password immediately

### Static File Verification

Verify static files are served correctly:
- Check that CSS loads (page should be styled)
- Check that JavaScript loads (interactive elements work)
- Verify images and other assets display

### Test Critical Flows

Test the following user flows:
1. User login and logout
2. Production entry
3. Payroll view
4. Payment recording
5. PDF export

## Vercel-Specific Considerations

### Static File Serving

Static files are served via Vercel CDN from `/public/` directory:
- CSS: `/public/css/style.css`
- JavaScript: `/public/js/hilltop.js`

The `static_url()` helper in templates automatically uses the correct path.

### Lambda Timeout

Vercel Python functions have a 10-second timeout:
- Optimize database queries
- Use efficient aggregation
- Cache frequently accessed data
- Monitor execution times

### File System Limitations

Vercel Lambda has no writable file system:
- Use in-memory operations for PDF generation
- Avoid writing temporary files
- Use BytesIO for PDF buffers
- All data must be stored in database

### Environment-Specific Behavior

The `VERCEL` environment variable is set to `1` automatically:
- Used by `static_url()` helper
- Enables production-specific behavior
- Disables debug mode

## Troubleshooting

### Build Failures

**Issue**: Build fails with dependency errors

**Solution**:
- Verify `requirements.txt` is complete
- Check for conflicting package versions
- Review build logs for specific errors

### Runtime Errors

**Issue**: Application returns 500 errors

**Solution**:
- Check environment variables are set correctly
- Verify database connection string format
- Review Vercel function logs
- Test database connectivity

### Database Connection Issues

**Issue**: Cannot connect to PostgreSQL

**Solution**:
- Verify DATABASE_URL format
- Check Supabase project status
- Ensure IP whitelisting if required
- Test connection string locally

### Static Files Not Loading

**Issue**: CSS and JavaScript not loading

**Solution**:
- Verify `/public/` directory structure
- Check `vercel.json` routes configuration
- Clear browser cache
- Verify file paths in templates

### Timeout Errors

**Issue**: Functions timeout after 10 seconds

**Solution**:
- Optimize slow database queries
- Use database indexes
- Implement caching where appropriate
- Consider Vercel Pro for longer timeouts

## Performance Optimization

### Database Query Optimization

- Use single queries with JOINs instead of N+1 queries
- Add indexes to frequently queried columns
- Use `EXPLAIN ANALYZE` to identify slow queries
- Consider read replicas for high traffic

### Caching Strategy

- Cache static assets with long TTL
- Use CDN for all static content
- Consider Redis for session storage
- Implement query result caching where appropriate

### Bundle Size Optimization

- Minimize JavaScript dependencies
- Use tree-shaking for unused code
- Optimize images and assets
- Consider lazy loading for non-critical resources

## Monitoring and Maintenance

### Vercel Analytics

Enable Vercel Analytics for:
- Page view tracking
- Performance monitoring
- User behavior insights
- Conversion tracking

### Error Tracking

Consider integrating error tracking:
- Sentry for error monitoring
- Log aggregation service
- Custom error logging
- Alert configuration

### Regular Maintenance

- Update dependencies regularly
- Review and optimize slow queries
- Monitor database size and performance
- Review security advisories

## Scaling Considerations

### When to Upgrade

Consider upgrading from free tier when:
- Exceeding 10-second function timeout
- Need custom domains
- Require advanced analytics
- Need dedicated support

### Cost Optimization

- Optimize function execution time
- Use efficient database queries
- Implement caching strategies
- Monitor and reduce unnecessary invocations

## Backup and Recovery

### Database Backups

Supabase provides automated backups:
- Daily backups included
- Point-in-time recovery available
- Export functionality for manual backups
- Consider additional backup strategy for critical data

### Disaster Recovery

- Document recovery procedures
- Test restore process regularly
- Maintain off-site backups
- Update recovery documentation

## Security Best Practices

### Environment Variables

- Never commit secrets to repository
- Rotate secrets regularly
- Use different secrets per environment
- Monitor for leaked credentials

### Access Control

- Implement proper authentication
- Use role-based access control
- Regular security audits
- Monitor access logs

### HTTPS Enforcement

- Vercel provides automatic HTTPS
- Redirect HTTP to HTTPS
- Use secure cookies
- Implement HSTS headers

## Support and Resources

### Vercel Documentation

- Official docs: https://vercel.com/docs
- Python runtime: https://vercel.com/docs/runtimes/python
- Environment variables: https://vercel.com/docs/projects/environment-variables

### Supabase Documentation

- Official docs: https://supabase.com/docs
- PostgreSQL: https://supabase.com/docs/guides/database
- Connection strings: https://supabase.com/docs/guides/database/connecting-to-postgres

### Community Support

- Vercel Discord: https://vercel.com/discord
- Supabase Discord: https://supabase.com/docs/guides/getting-started/discord
- GitHub Issues: Project repository issues

This deployment guide ensures successful deployment of the Hilltop Tea system to Vercel with proper configuration, monitoring, and maintenance procedures.
