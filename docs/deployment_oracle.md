# Oracle Cloud Free Tier Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Hilltop Tea Wage Tracking & Payroll System to Oracle Cloud Free Tier. Oracle Cloud provides generous free resources including virtual machines and autonomous database.

## Prerequisites

- Oracle Cloud account (free tier available)
- Basic familiarity with Linux command line
- SSH access knowledge
- Domain name (optional, for custom domain)

## Preparation

### 1. Oracle Cloud Free Tier Resources

Oracle Cloud Free Tier includes:
- **Compute**: 2 AMD-based VMs with 1/8 OCPU each
- **Database**: 2 Autonomous Databases (20GB each)
- **Storage**: 2 Block Volumes (100GB total)
- **Bandwidth**: 10TB/month outbound data transfer

### 2. Required Software

Ensure you have:
- SSH client
- Text editor
- Git
- Python 3.11+ (will be installed on VM)

## Deployment Steps

### Step 1: Create Oracle Cloud Account

1. Visit https://www.oracle.com/cloud/free/
2. Click "Sign Up"
3. Complete registration process
4. Verify email address
5. Log in to Oracle Cloud Console

### Step 2: Create Virtual Machine

1. Navigate to Compute → Instances
2. Click "Create Instance"
3. Configure the instance:

**Name**: `hilltop-tea-app`

**Compartment**: Select your compartment

**Shape**:
- Choose "Always Free" eligible shape
- VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM)

**Image**:
- Operating System: Oracle Linux
- Version: 8 or 9

**Networking**:
- Use virtual cloud network (VCN)
- Assign public IP address
- Create SSH key pair

4. Click "Create"

### Step 3: Create Autonomous Database

1. Navigate to Oracle Database → Autonomous Database
2. Click "Create Autonomous Database"
3. Configure the database:

**Display Name**: `hilltop-tea-db`

**Compartment**: Select your compartment

**Workload Type**: Transaction Processing

**Database Name**: `hilltop`

**Admin Password**: Generate strong password

**Compute Model**: Serverless

**Storage**: 20 GB (Always Free)

**License**: Bring Your Own License (BYOL) or Included

4. Click "Create Autonomous Database"

5. Note the connection details:
   - Database connection string
   - Admin username
   - Wallet file (download)

### Step 4: Configure Security

1. Navigate to Networking → Virtual Cloud Networks
2. Select your VCN
3. Configure Security List:
   - Allow TCP port 22 (SSH)
   - Allow TCP port 80 (HTTP)
   - Allow TCP port 443 (HTTPS)

4. Configure Security Rules:
   - Add ingress rule for port 80 from 0.0.0.0/0
   - Add ingress rule for port 443 from 0.0.0.0/0

### Step 5: Connect to VM

1. Download the private key from Oracle Cloud
2. Set proper permissions:
   ```bash
   chmod 600 your-key.pem
   ```

3. Connect via SSH:
   ```bash
   ssh -i your-key.pem opc@your-vm-public-ip
   ```

### Step 6: Install Dependencies

1. Update system:
   ```bash
   sudo dnf update -y
   ```

2. Install Python and dependencies:
   ```bash
   sudo dnf install -y python3 python3-pip git
   ```

3. Install additional packages:
   ```bash
   sudo dnf install -y postgresql-devel gcc
   ```

### Step 7: Deploy Application

1. Clone repository:
   ```bash
   cd /home/opc
   git clone https://github.com/yourusername/hilltop_tea.git
   cd hilltop_tea
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   nano .env
   ```

5. Configure environment variables:
   ```
   SECRET_KEY=your-generated-secret-key
   DATABASE_URL=postgresql+psycopg2://user:password@host:port/database
   FLASK_ENV=production
   PORT=5000
   ```

### Step 8: Initialize Database

1. Run database migrations:
   ```bash
   flask db upgrade
   ```

2. Seed admin user:
   ```bash
   flask shell
   >>> from run import _seed_admin
   _seed_admin()
   >>> exit()
   ```

### Step 9: Configure Systemd Service

1. Create systemd service file:
   ```bash
   sudo nano /etc/systemd/system/hilltop-tea.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=Hilltop Tea Application
   After=network.target

   [Service]
   User=opc
   Group=opc
   WorkingDirectory=/home/opc/hilltop_tea
   Environment="PATH=/home/opc/hilltop_tea/venv/bin"
   ExecStart=/home/opc/hilltop_tea/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 run:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable hilltop-tea
   sudo systemctl start hilltop-tea
   ```

4. Check status:
   ```bash
   sudo systemctl status hilltop-tea
   ```

### Step 10: Configure Nginx (Optional)

1. Install Nginx:
   ```bash
   sudo dnf install -y nginx
   ```

2. Configure Nginx:
   ```bash
   sudo nano /etc/nginx/nginx.conf
   ```

3. Add reverse proxy configuration:
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

4. Start Nginx:
   ```bash
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

## Post-Deployment Configuration

### Domain Configuration

1. Purchase domain (if needed)
2. Configure DNS records:
   - A record pointing to VM public IP
   - CNAME for www subdomain

3. Configure Nginx for domain:
   ```nginx
   server {
       listen 80;
       server_name hilltop-tea.example.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### SSL Certificate

1. Install Certbot:
   ```bash
   sudo dnf install -y certbot python3-certbot-nginx
   ```

2. Obtain certificate:
   ```bash
   sudo certbot --nginx -d hilltop-tea.example.com
   ```

3. Auto-renewal is configured automatically

### Monitoring Setup

1. Install monitoring tools:
   ```bash
   sudo dnf install -y htop
   ```

2. Configure log rotation:
   ```bash
   sudo nano /etc/logrotate.d/hilltop-tea
   ```

3. Add log rotation configuration:
   ```
   /home/opc/hilltop_tea/logs/*.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

## Oracle Cloud-Specific Considerations

### Resource Limits

Free tier limitations:
- 2 AMD VMs with 1/8 OCPU each
- 2 Autonomous Databases (20GB each)
- 100GB block storage
- 10TB/month outbound transfer

### Always Free Resources

- Compute: 2 VM.Standard.E2.1.Micro instances
- Storage: 2 Block Volumes (up to 100GB total)
- Database: 2 Autonomous Databases (20GB each)
- Network: 10TB/month outbound data transfer

### Autonomous Database Features

- Automatic scaling
- Backup and recovery
- High availability
- Security features
- Performance monitoring

## Troubleshooting

### VM Connection Issues

**Issue**: Cannot connect via SSH

**Solution**:
- Verify public IP is correct
- Check security list rules
- Verify SSH key permissions
- Check VM status in console

### Database Connection Issues

**Issue**: Cannot connect to Autonomous Database

**Solution**:
- Verify connection string format
- Check wallet file is correct
- Verify network access rules
- Test connection locally

### Service Not Starting

**Issue**: Systemd service fails to start

**Solution**:
- Check service logs: `sudo journalctl -u hilltop-tea`
- Verify environment variables
- Check file permissions
- Review error messages

### Out of Memory Errors

**Issue**: VM runs out of memory

**Solution**:
- Reduce worker count
- Optimize memory usage
- Add swap space
- Consider upgrading to paid tier

### Slow Performance

**Issue**: Application is slow

**Solution**:
- Optimize database queries
- Add database indexes
- Increase worker count
- Consider upgrading resources

## Performance Optimization

### Database Optimization

- Use connection pooling
- Optimize slow queries
- Add appropriate indexes
- Monitor database performance

### Application Optimization

- Use efficient query patterns
- Implement caching
- Optimize worker configuration
- Monitor resource usage

### Network Optimization

- Use CDN for static assets
- Enable compression
- Optimize image sizes
- Minimize HTTP requests

## Monitoring and Maintenance

### Oracle Cloud Monitoring

- Monitor CPU usage
- Track memory usage
- Monitor network traffic
- Review storage usage

### Log Management

- Review application logs
- Monitor error logs
- Set up log rotation
- Archive old logs

### Regular Maintenance

- Update system packages
- Update Python dependencies
- Review security advisories
- Test backup and recovery

## Backup and Recovery

### Database Backups

Oracle Autonomous Database provides:
- Automatic daily backups
- 7-day retention (free tier)
- Point-in-time recovery
- Manual backup options

### Application Backups

1. Backup application files:
   ```bash
   tar -czf hilltop-tea-backup.tar.gz /home/opc/hilltop_tea
   ```

2. Backup to Object Storage:
   ```bash
   oci os object put --bucket your-bucket --file hilltop-tea-backup.tar.gz
   ```

### Disaster Recovery

- Document recovery procedures
- Test restore process regularly
- Maintain off-site backups
- Update recovery documentation

## Security Best Practices

### VM Security

- Keep system updated
- Use strong SSH keys
- Disable password authentication
- Configure firewall rules

### Database Security

- Use strong passwords
- Enable encryption
- Restrict access
- Regular security updates

### Network Security

- Use HTTPS
- Configure firewall
- Monitor access logs
- Implement rate limiting

## Cost Management

### Free Tier Limits

- 2 VMs with 1/8 OCPU each
- 2 Autonomous Databases (20GB each)
- 100GB block storage
- 10TB/month outbound transfer

### When to Upgrade

Consider upgrading when:
- Exceeding resource limits
- Need more storage
- Require better performance
- Need additional features

### Cost Optimization

- Optimize resource usage
- Use efficient queries
- Implement caching
- Monitor and reduce waste

## Support and Resources

### Oracle Cloud Documentation

- Official docs: https://docs.oracle.com/en-us/iaas
- Compute: https://docs.oracle.com/en-us/iaas/Compute
- Database: https://docs.oracle.com/en-us/iaas/Database

### Community Support

- Oracle Community: https://community.oracle.com
- Stack Overflow: Tag with `oracle-cloud`
- GitHub: Oracle Cloud repositories

### Additional Resources

- Oracle Cloud Free Tier: https://www.oracle.com/cloud/free/
- Tutorials: https://learn.oracle.com
- Blog: https://blogs.oracle.com/cloud

This deployment guide ensures successful deployment of the Hilltop Tea system to Oracle Cloud Free Tier with proper configuration, monitoring, and maintenance procedures.
