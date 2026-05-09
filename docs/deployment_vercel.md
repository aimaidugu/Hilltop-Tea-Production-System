# HILLTOP TEA — Vercel Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying Hilltop Tea to Vercel. Vercel is a serverless platform optimized for frontend and serverless functions, making it an excellent choice for Flask applications with static assets.

## Prerequisites

- Vercel account (free tier is sufficient)
- GitHub repository with the Hilltop Tea code
- PostgreSQL database (Vercel Postgres or external provider)

## Step 1: Prepare Your Repository

Ensure your repository includes all necessary files:

- `api/index.py` - Vercel entry point
- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `public/` directory - Static files (mirrored from `app/static/`)

## Step 2: Set Up PostgreSQL Database

### Option A: Vercel Postgres

1. Navigate to your Vercel project dashboard
2. Go to the Storage tab
3. Click "Create Database"
4. Select "Postgres" and choose a region
5. Note the connection string from the database details

### Option B: External PostgreSQL

1. Create a PostgreSQL database on your preferred provider
2. Obtain the connection string in the format:
   `postgresql://username:password@host:port/database`

## Step 3: Configure Environment Variables

1. Navigate to your Vercel project dashboard
2. Go to the Settings tab
3. Select Environment Variables
4. Add the following variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `SECRET_KEY` | Generate with `openssl rand -hex 32` | Production |
| `DATABASE_URL` | Your PostgreSQL connection string | Production |
| `FLASK_ENV` | `production` | Production |
| `VERCEL` | `1` | Production |

## Step 4: Copy Static Files to Public Directory

Vercel serves static files from the `public/` directory via CDN. Before deployment, copy your static files:

```bash
cp -r app/static/* public/
```

For automated copying, add this to your `package.json` or create a build script:

```bash
# In vercel.json build command
"build": "cp -r app/static/* public/"
```

## Step 5: Deploy to Vercel

### Via Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Follow the prompts to configure your project

### Via GitHub Integration

1. Push your code to GitHub
2. Import your repository in Vercel
3. Configure build settings (Vercel will detect Python automatically)
4. Deploy

## Step 6: Run Database Migrations

After first deployment, initialize the database schema:

1. Open your Vercel project dashboard
2. Go to the Functions tab
3. Click "Create Function" or use the CLI:
   ```bash
   vercel env pull .env.local
   source .env.local
   flask db upgrade
   ```

4. Seed the admin account:
   ```bash
   flask shell -c "from run import _seed_admin; _seed_admin()"
   ```

## Step 7: Verify Deployment

1. Visit your Vercel deployment URL
2. Log in with the default credentials (admin / admin123)
3. Change the default password immediately
4. Test key functionality:
   - Dashboard loads correctly
   - Production entry works
   - Payroll view displays data
   - PDF export generates correctly

## Configuration Details

### vercel.json

The `vercel.json` file configures how Vercel handles your application:

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "30mb" }
    }
  ],
  "routes": [
    {
      "src": "/public/(.*)",
      "dest": "/public/$1",
      "headers": { "Cache-Control": "public, max-age=31536000, immutable" }
    },
    { "src": "/(.*)", "dest": "/api/index.py" }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
```

### Static File Handling

Static files are served from the `/public/` path via Vercel's CDN. The `static_url()` context processor in `app/__init__.py` handles the URL difference:

```python
@app.context_processor
def inject_static():
    import os
    is_vercel = os.environ.get('VERCEL') == '1'

    def static_url(path):
        if is_vercel:
            return f'/public/{path}'
        from flask import url_for
        return url_for('static', filename=path)

    return dict(static_url=static_url)
```

## Troubleshooting

### Issue: Static files not loading

**Solution:** Ensure static files are copied to the `public/` directory before deployment. Verify the `static_url()` function is returning the correct path.

### Issue: Database connection errors

**Solution:** Verify the `DATABASE_URL` environment variable is set correctly. Ensure the PostgreSQL database is accessible from Vercel's network.

### Issue: Lambda timeout

**Solution:** Increase the `maxLambdaSize` in `vercel.json` or optimize database queries. The payroll view uses a single query to avoid timeouts.

### Issue: CSRF token errors

**Solution:** Ensure `WTF_CSRF_ENABLED` is set to `True` in production. Verify the `SECRET_KEY` is set and consistent across requests.

## Performance Optimization

### Enable Caching

Static files are cached for one year by default. For dynamic content, consider implementing caching for frequently accessed data.

### Optimize Database Queries

The payroll view uses a single aggregation query to avoid N+1 problems. Ensure all queries use appropriate indexes.

### Monitor Lambda Execution

Vercel provides execution time metrics. Monitor these to identify slow routes and optimize accordingly.

## Security Considerations

1. **HTTPS Only:** Vercel automatically provisions SSL certificates
2. **Secure Cookies:** Session cookies are marked as secure in production
3. **Environment Variables:** Never commit secrets to version control
4. **Rate Limiting:** Consider implementing rate limiting for API endpoints

## Scaling

Vercel automatically scales based on traffic. For high-traffic scenarios:

1. Consider using Vercel's Pro plan for higher limits
2. Implement caching for frequently accessed data
3. Use a connection pooler for PostgreSQL
4. Monitor Lambda execution times and optimize slow routes

## Cost Considerations

Vercel's free tier includes:
- 100GB bandwidth per month
- 6,000 minutes of execution time per month
- Unlimited projects

For production use, consider the Pro plan ($20/month) for:
- 1TB bandwidth
- 100,000 minutes of execution time
- Priority support
