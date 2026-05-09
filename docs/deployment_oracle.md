# HILLTOP TEA — Oracle Cloud Free Tier Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying Hilltop Tea to Oracle Cloud Free Tier. Oracle Cloud Free Tier provides always-free compute and database resources, making it an excellent option for hosting production applications.

## Prerequisites

- Oracle Cloud account (free tier is sufficient)
- GitHub repository with the Hilltop Tea code
- SSH client
- Basic knowledge of Linux command line

## Step 1: Create Oracle Cloud Account

1. Visit cloud.oracle.com
2. Sign up for a free account
3. Verify your email address
4. Add a payment method (required for free tier, but not charged)

## Step 2: Provision Compute Instance

1. Log in to Oracle Cloud Console
2. Navigate to "Compute" → "Instances"
3. Click "Create Instance"
4. Configure the instance:

   **Name:** hilltop-tea-app
   **Compartment:** Select your compartment
   **Availability Domain:** Any available domain
   **Shape:** VM.Standard.E2.1.Micro (Always Free)
   **Operating System:** Oracle Linux or Ubuntu
   **SSH Keys:** Upload your public SSH key

5. Click "Create"

## Step 3: Provision Autonomous Database

1. Navigate to "Oracle Database" → "Autonomous Transaction Processing"
2. Click "Create Autonomous Database"
3. Configure the database:

   **Display Name:** hilltop-tea-db
   **Compartment:** Select your compartment
   **CPU Core Count:** 1 OCPU (Always Free)
   **Storage:** 20 GB (Always Free)
   **Admin Password:** Set a secure password
   **License:** Bring Your Own License (BYOL)

4. Click "Create Autonomous Database"

5. Wait for provisioning to complete

6. Download the wallet:
   - Click on your database
   - Go to "Connection" → "Wallet Download"
   - Download and extract the wallet

## Step 4: Configure Compute Instance

### SSH into the Instance

```bash
ssh -i /path/to/your/key opc@<public-ip-address>
```

### Update System

```bash
sudo yum update -y
```

### Install Python 3.11

```bash
sudo yum install -y python3.11 python3.11-pip python3.11-devel
```

### Install PostgreSQL Client

```bash
sudo yum install -y postgresql
```

### Clone Repository

```bash
cd /opt
sudo git clone https://github.com/yourusername/hilltop_tea.git
sudo chown -R opc:opc hilltop_tea
cd hilltop_tea
```

### Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

```bash
sudo nano /etc/systemd/system/hilltop_tea.env
```

Add the following:

```bash
SECRET_KEY=<generate-with-openssl-rand-hex-32>
FLASK_ENV=production
DATABASE_URL=postgresql+psycopg2://<username>:<password>@<host>:<port>/<database>
PORT=5000
```

Replace the database connection string with your Autonomous Database details.

### Configure PostgreSQL Wallet

```bash
mkdir -p ~/.postgresql
cp /path/to/wallet/* ~/.postgresql/
chmod 600 ~/.postgresql/*
```

Update `~/.bashrc`:

```bash
export LD_LIBRARY_PATH=/usr/lib/oracle/21/client64/lib
export TNS_ADMIN=~/.postgresql
```

## Step 5: Initialize Database

```bash
source venv/bin/activate
export $(cat /etc/systemd/system/hilltop_tea.env | xargs)
flask db upgrade
flask shell -c "from run import _seed_admin; _seed_admin()"
```

## Step 6: Configure Systemd Service

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/hilltop_tea.service
```

Add the following:

```ini
[Unit]
Description=Hilltop Tea Application
After=network.target

[Service]
Type=notify
User=opc
Group=opc
WorkingDirectory=/opt/hilltop_tea
Environment="PATH=/opt/hilltop_tea/venv/bin"
EnvironmentFile=/etc/systemd/system/hilltop_tea.env
ExecStart=/opt/hilltop_tea/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hilltop_tea
sudo systemctl start hilltop_tea
sudo systemctl status hilltop_tea
```

## Step 7: Configure Firewall

### Open Port 5000

```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### Configure Oracle Cloud Security List

1. Navigate to "Networking" → "Virtual Cloud Networks"
2. Select your VCN
3. Go to "Security Lists"
4. Add an ingress rule:
   - Source: 0.0.0.0/0
   - IP Protocol: TCP
- Destination Port: 5000

## Step 8: Configure Nginx (Optional)

For production, use Nginx as a reverse proxy:

### Install Nginx

```bash
sudo yum install -y nginx
```

### Configure Nginx

```bash
sudo nano /etc/nginx/conf.d/hilltop_tea.conf
```

Add the following:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Start Nginx:

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

## Step 9: Configure SSL (Optional)

Use Let's Encrypt for free SSL:

```bash
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Step 10: Verify Deployment

1. Visit your instance's public IP address or domain
2. Log in with the default credentials (admin / admin123)
3. Change the default password immediately
4. Test key functionality

## Configuration Details

### Procfile

The Procfile tells the system how to start your application:

```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app
```

### nixpacks.toml

Nixpacks handles the build environment:

```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 run:app"
```

## Troubleshooting

### Issue: Database connection fails

**Solution:** Verify the Autonomous Database wallet is correctly configured. Check that the `TNS_ADMIN` environment variable is set. Ensure the database connection string is correct.

### Issue: Service fails to start

**Solution:** Check the service logs:
```bash
sudo journalctl -u hilltop_tea -f
```

Verify all environment variables are set correctly.

### Issue: Port not accessible

**Solution:** Verify the firewall rules and Oracle Cloud security list. Ensure the instance's public IP is correct.

### Issue: Out of memory errors

**Solution:** The Always Free tier has limited RAM. Consider reducing the number of workers or using threads instead:
```bash
ExecStart=/opt/hilltop_tea/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 4 --timeout 60 run:app
```

## Performance Optimization

### Worker Configuration

Adjust based on available resources:

```bash
# For Always Free tier (1 OCPU, 1GB RAM)
ExecStart=/opt/hilltop_tea/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 4 --timeout 60 run:app
```

### Database Connection Pooling

Configure SQLAlchemy for optimal performance:

```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 3600,
}
```

### Caching

Consider implementing caching for frequently accessed data:

```bash
pip install redis
```

## Security Considerations

1. **SSH Keys:** Use SSH keys instead of password authentication
2. **Firewall:** Only open necessary ports
3. **Updates:** Keep the system updated
4. **SSL:** Use HTTPS in production
5. **Secrets:** Never commit secrets to version control

## Scaling

Oracle Cloud Free Tier has fixed resources. For scaling:

1. **Upgrade Plan:** Consider paid tiers for more resources
2. **Horizontal Scaling:** Add more compute instances
3. **Load Balancing:** Use Oracle Cloud Load Balancer
4. **Database Scaling:** Upgrade Autonomous Database instance

## Cost Considerations

Oracle Cloud Free Tier includes:
- 2 AMD-based compute instances (1 OCPU each)
- 4 Arm-based compute instances (up to 4 OCPUs each)
- 200 GB of block storage
- 20 GB of Autonomous Database
- 10 TB of outbound data transfer per month

For production use, consider paid tiers for:
- More compute resources
- Higher database performance
- Additional storage
- Priority support

## Backup and Recovery

### Database Backups

Oracle Autonomous Database automatically creates backups. To restore:

1. Navigate to your database
2. Go to "Backups"
3. Select a backup to restore

### Manual Backup

```bash
# From compute instance
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Application Backup

```bash
# Backup application files
tar -czf hilltop_tea_backup.tar.gz /opt/hilltop_tea

# Restore
tar -xzf hilltop_tea_backup.tar.gz -C /
```

## Monitoring

### Application Logs

View service logs:

```bash
sudo journalctl -u hilltop_tea -f
```

### Database Metrics

Monitor Autonomous Database performance in the Oracle Cloud Console.

### System Metrics

Use Oracle Cloud Monitoring or install tools:

```bash
sudo yum install -y htop
```

## Maintenance

### Update Application

```bash
cd /opt/hilltop_tea
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart hilltop_tea
```

### Database Migrations

```bash
source venv/bin/activate
export $(cat /etc/systemd/system/hilltop_tea.env | xargs)
flask db upgrade
```

### Log Rotation

Configure logrotate:

```bash
sudo nano /etc/logrotate.d/hilltop_tea
```

Add:

```
/var/log/hilltop_tea/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 opc opc
}
```
