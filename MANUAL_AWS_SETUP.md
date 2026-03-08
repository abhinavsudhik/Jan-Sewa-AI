# Manual AWS Setup Guide

This guide walks you through deploying your application to AWS manually using the AWS Console, without requiring Terraform.

## Prerequisites

- AWS Account (create one at https://aws.amazon.com/)
- AWS CLI installed (optional but helpful)
- Docker installed locally
- Your application code ready

---

## Phase 1: Set Up Networking (VPC)

### Step 1.1: Create VPC

1. Go to **AWS Console** → **VPC** → **Your VPCs**
2. Click **Create VPC**
3. Configure:
   - **Name**: `govt-services-vpc`
   - **IPv4 CIDR**: `10.0.0.0/16`
   - **IPv6 CIDR**: No IPv6 CIDR block
   - **Tenancy**: Default
4. Click **Create VPC**

### Step 1.2: Create Subnets

**Public Subnet 1:**
1. Go to **Subnets** → **Create subnet**
2. Configure:
   - **VPC**: Select `govt-services-vpc`
   - **Name**: `govt-services-public-1`
   - **Availability Zone**: `us-east-1a`
   - **IPv4 CIDR**: `10.0.0.0/24`
3. Click **Create subnet**

**Public Subnet 2:**
1. Repeat above with:
   - **Name**: `govt-services-public-2`
   - **Availability Zone**: `us-east-1b`
   - **IPv4 CIDR**: `10.0.1.0/24`

**Private Subnet 1:**
1. Create subnet:
   - **Name**: `govt-services-private-1`
   - **Availability Zone**: `us-east-1a`
   - **IPv4 CIDR**: `10.0.10.0/24`

**Private Subnet 2:**
1. Create subnet:
   - **Name**: `govt-services-private-2`
   - **Availability Zone**: `us-east-1b`
   - **IPv4 CIDR**: `10.0.11.0/24`

### Step 1.3: Create Internet Gateway

1. Go to **Internet Gateways** → **Create internet gateway**
2. **Name**: `govt-services-igw`
3. Click **Create**
4. Select the gateway → **Actions** → **Attach to VPC**
5. Select `govt-services-vpc` → **Attach**

### Step 1.4: Create NAT Gateway

1. Go to **NAT Gateways** → **Create NAT gateway**
2. Configure:
   - **Name**: `govt-services-nat`
   - **Subnet**: Select `govt-services-public-1`
   - **Elastic IP**: Click **Allocate Elastic IP**
3. Click **Create NAT gateway**

### Step 1.5: Create Route Tables

**Public Route Table:**
1. Go to **Route Tables** → **Create route table**
2. Configure:
   - **Name**: `govt-services-public-rt`
   - **VPC**: `govt-services-vpc`
3. Click **Create**
4. Select the route table → **Routes** tab → **Edit routes**
5. Add route:
   - **Destination**: `0.0.0.0/0`
   - **Target**: Select Internet Gateway (`govt-services-igw`)
6. **Subnet Associations** tab → **Edit subnet associations**
7. Select both public subnets → **Save**

**Private Route Table:**
1. Create route table:
   - **Name**: `govt-services-private-rt`
   - **VPC**: `govt-services-vpc`
2. Add route:
   - **Destination**: `0.0.0.0/0`
   - **Target**: Select NAT Gateway (`govt-services-nat`)
3. Associate with both private subnets

---

## Phase 2: Set Up Database (RDS)

### Step 2.1: Create DB Subnet Group

1. Go to **RDS** → **Subnet groups** → **Create DB subnet group**
2. Configure:
   - **Name**: `govt-services-db-subnet`
   - **VPC**: `govt-services-vpc`
   - **Availability Zones**: Select `us-east-1a` and `us-east-1b`
   - **Subnets**: Select both private subnets
3. Click **Create**

### Step 2.2: Create Security Group for Database

1. Go to **EC2** → **Security Groups** → **Create security group**
2. Configure:
   - **Name**: `govt-services-db-sg`
   - **Description**: Security group for RDS PostgreSQL
   - **VPC**: `govt-services-vpc`
3. **Inbound rules**: Leave empty for now (we'll add after creating ECS security group)
4. Click **Create**

### Step 2.3: Create RDS PostgreSQL Database

1. Go to **RDS** → **Databases** → **Create database**
2. Configure:
   - **Engine**: PostgreSQL
   - **Version**: PostgreSQL 15.4
   - **Templates**: Free tier
   - **DB instance identifier**: `govt-services-db`
   - **Master username**: `admin`
   - **Master password**: Create a strong password (save this!)
   - **DB instance class**: `db.t3.micro`
   - **Storage**: 20 GB (General Purpose SSD)
   - **VPC**: `govt-services-vpc`
   - **Subnet group**: `govt-services-db-subnet`
   - **Public access**: No
   - **VPC security group**: Select `govt-services-db-sg`
   - **Database name**: `govt_services`
   - **Backup retention**: 7 days
   - **Encryption**: Enable
3. Click **Create database**

**⏱️ This takes 10-15 minutes. Continue with other steps while it's creating.**

### Step 2.4: Store Database Credentials in Secrets Manager

1. Go to **Secrets Manager** → **Store a new secret**
2. Configure:
   - **Secret type**: Other type of secret
   - **Key/value pairs**:
     ```
     DATABASE_URL: postgresql://admin:YOUR_PASSWORD@YOUR_DB_ENDPOINT:5432/govt_services
     SECRET_KEY: (generate a random 64-character string)
     GEMINI_API_KEY: your-gemini-api-key
     ```
   - **Secret name**: `govt-services/backend/prod`
3. Click **Store**

---

## Phase 3: Set Up Container Registry (ECR)

### Step 3.1: Create ECR Repository

1. Go to **ECR** → **Repositories** → **Create repository**
2. Configure:
   - **Visibility**: Private
   - **Repository name**: `govt-services-backend`
   - **Image scanning**: Enable scan on push
3. Click **Create repository**

### Step 3.2: Build and Push Docker Image

```bash
# Get ECR login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
cd backend
docker build -t govt-services-backend:latest -f Dockerfile.prod .

# Tag image
docker tag govt-services-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/govt-services-backend:latest

# Push image
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/govt-services-backend:latest
```

Replace `YOUR_ACCOUNT_ID` with your AWS account ID (find it in AWS Console top right).

---

## Phase 4: Set Up ECS (Container Service)

### Step 4.1: Create ECS Cluster

1. Go to **ECS** → **Clusters** → **Create cluster**
2. Configure:
   - **Cluster name**: `govt-services-cluster`
   - **Infrastructure**: AWS Fargate
3. Click **Create**

### Step 4.2: Create Security Groups

**ALB Security Group:**
1. Go to **EC2** → **Security Groups** → **Create security group**
2. Configure:
   - **Name**: `govt-services-alb-sg`
   - **VPC**: `govt-services-vpc`
   - **Inbound rules**:
     - Type: HTTP, Port: 80, Source: 0.0.0.0/0
     - Type: HTTPS, Port: 443, Source: 0.0.0.0/0
3. Click **Create**

**ECS Security Group:**
1. Create security group:
   - **Name**: `govt-services-ecs-sg`
   - **VPC**: `govt-services-vpc`
   - **Inbound rules**:
     - Type: Custom TCP, Port: 8000, Source: `govt-services-alb-sg`
2. Click **Create**

**Update Database Security Group:**
1. Go to `govt-services-db-sg` → **Edit inbound rules**
2. Add rule:
   - Type: PostgreSQL, Port: 5432, Source: `govt-services-ecs-sg`
3. Save

### Step 4.3: Create IAM Roles

**ECS Task Execution Role:**
1. Go to **IAM** → **Roles** → **Create role**
2. Configure:
   - **Trusted entity**: AWS service → ECS → ECS Task
   - **Permissions**: 
     - `AmazonECSTaskExecutionRolePolicy`
     - Create inline policy for Secrets Manager:
       ```json
       {
         "Version": "2012-10-17",
         "Statement": [
           {
             "Effect": "Allow",
             "Action": "secretsmanager:GetSecretValue",
             "Resource": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:govt-services/backend/prod*"
           }
         ]
       }
       ```
   - **Role name**: `govt-services-ecs-execution-role`
3. Click **Create role**

**ECS Task Role:**
1. Create another role:
   - **Trusted entity**: AWS service → ECS → ECS Task
   - **Permissions**: Create inline policy:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": [
             "logs:CreateLogStream",
             "logs:PutLogEvents"
           ],
           "Resource": "*"
         }
       ]
     }
     ```
   - **Role name**: `govt-services-ecs-task-role`

### Step 4.4: Create CloudWatch Log Group

1. Go to **CloudWatch** → **Log groups** → **Create log group**
2. **Name**: `/ecs/govt-services-backend`
3. **Retention**: 7 days
4. Click **Create**

### Step 4.5: Create Application Load Balancer

1. Go to **EC2** → **Load Balancers** → **Create load balancer**
2. Select **Application Load Balancer**
3. Configure:
   - **Name**: `govt-services-alb`
   - **Scheme**: Internet-facing
   - **VPC**: `govt-services-vpc`
   - **Subnets**: Select both public subnets
   - **Security group**: `govt-services-alb-sg`
4. **Listeners**: HTTP on port 80
5. Click **Create load balancer**

### Step 4.6: Create Target Group

1. Go to **EC2** → **Target Groups** → **Create target group**
2. Configure:
   - **Target type**: IP addresses
   - **Name**: `govt-services-tg`
   - **Protocol**: HTTP
   - **Port**: 8000
   - **VPC**: `govt-services-vpc`
   - **Health check path**: `/health`
   - **Health check interval**: 30 seconds
3. Click **Create**

### Step 4.7: Update ALB Listener

1. Go to your ALB → **Listeners** tab
2. Select HTTP:80 listener → **Edit**
3. **Default action**: Forward to `govt-services-tg`
4. Save

### Step 4.8: Create ECS Task Definition

1. Go to **ECS** → **Task Definitions** → **Create new task definition**
2. Configure:
   - **Family**: `govt-services-backend`
   - **Launch type**: Fargate
   - **OS**: Linux
   - **CPU**: 0.25 vCPU
   - **Memory**: 0.5 GB
   - **Task execution role**: `govt-services-ecs-execution-role`
   - **Task role**: `govt-services-ecs-task-role`
3. **Container**:
   - **Name**: `backend`
   - **Image**: `YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/govt-services-backend:latest`
   - **Port mappings**: 8000 TCP
   - **Environment variables**:
     - `ENVIRONMENT`: `prod`
   - **Secrets** (from Secrets Manager):
     - `DATABASE_URL`: `govt-services/backend/prod:DATABASE_URL::`
     - `SECRET_KEY`: `govt-services/backend/prod:SECRET_KEY::`
     - `GEMINI_API_KEY`: `govt-services/backend/prod:GEMINI_API_KEY::`
   - **Log configuration**:
     - Log driver: awslogs
     - Log group: `/ecs/govt-services-backend`
     - Region: `us-east-1`
     - Stream prefix: `ecs`
4. Click **Create**

### Step 4.9: Create ECS Service

1. Go to your cluster → **Services** tab → **Create**
2. Configure:
   - **Launch type**: Fargate
   - **Task definition**: `govt-services-backend` (latest)
   - **Service name**: `govt-services-backend-service`
   - **Desired tasks**: 1
   - **VPC**: `govt-services-vpc`
   - **Subnets**: Select both private subnets
   - **Security group**: `govt-services-ecs-sg`
   - **Load balancer**: Application Load Balancer
   - **Load balancer name**: `govt-services-alb`
   - **Target group**: `govt-services-tg`
   - **Health check grace period**: 60 seconds
3. Click **Create**

**⏱️ Wait 5-10 minutes for the service to start and become healthy.**

### Step 4.10: Test Backend

1. Go to your ALB → Copy DNS name
2. Test: `curl http://YOUR_ALB_DNS/health`
3. Should return: `{"status":"healthy"}`

---

## Phase 5: Set Up Frontend (S3 + CloudFront)

### Step 5.1: Create S3 Bucket

1. Go to **S3** → **Create bucket**
2. Configure:
   - **Name**: `govt-services-frontend-prod` (must be globally unique)
   - **Region**: us-east-1
   - **Block all public access**: Keep checked
   - **Versioning**: Enable
3. Click **Create bucket**

### Step 5.2: Create CloudFront Distribution

1. Go to **CloudFront** → **Create distribution**
2. **Origin**:
   - **Origin domain**: Select your S3 bucket
   - **Origin access**: Origin access control settings
   - Click **Create control setting** → Create
3. **Default cache behavior**:
   - **Viewer protocol policy**: Redirect HTTP to HTTPS
   - **Allowed HTTP methods**: GET, HEAD, OPTIONS
   - **Cache policy**: CachingOptimized
4. **Settings**:
   - **Price class**: Use only North America and Europe
   - **Default root object**: `index.html`
5. **Custom error responses** (add after creation):
   - Error code: 404 → Response: 200, Path: `/index.html`
   - Error code: 403 → Response: 200, Path: `/index.html`
6. Click **Create distribution**

### Step 5.3: Update S3 Bucket Policy

1. Go to your S3 bucket → **Permissions** → **Bucket policy**
2. CloudFront will show you a policy to copy - paste it
3. Save

### Step 5.4: Build and Deploy Frontend

```bash
cd frontend

# Get your ALB DNS name
ALB_DNS="your-alb-dns-name.us-east-1.elb.amazonaws.com"

# Build frontend
NEXT_PUBLIC_API_URL=http://$ALB_DNS npm run build

# Deploy to S3
aws s3 sync out/ s3://govt-services-frontend-prod/ --delete

# Get CloudFront distribution ID
DIST_ID="your-distribution-id"

# Invalidate cache
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

### Step 5.5: Access Your Application

1. Go to CloudFront → Your distribution → Copy domain name
2. Open in browser: `https://YOUR_CLOUDFRONT_DOMAIN`

---

## Phase 6: Set Up Monitoring

### Step 6.1: Create SNS Topic for Alerts

1. Go to **SNS** → **Topics** → **Create topic**
2. Configure:
   - **Type**: Standard
   - **Name**: `govt-services-alerts`
3. Click **Create topic**
4. **Create subscription**:
   - **Protocol**: Email
   - **Endpoint**: your-email@example.com
5. Check your email and confirm subscription

### Step 6.2: Create CloudWatch Alarms

**Backend CPU Alarm:**
1. Go to **CloudWatch** → **Alarms** → **Create alarm**
2. **Metric**: ECS → By Cluster, Service → CPUUtilization
3. Configure:
   - **Threshold**: Greater than 80%
   - **Period**: 5 minutes
   - **Datapoints**: 2 out of 2
   - **Notification**: Select SNS topic `govt-services-alerts`
   - **Name**: `backend-cpu-high`
4. Create alarm

**Backend Errors Alarm:**
1. Create alarm:
   - **Metric**: ApplicationELB → HTTPCode_Target_5XX_Count
   - **Threshold**: Greater than 10
   - **Period**: 5 minutes
   - **Notification**: `govt-services-alerts`
   - **Name**: `backend-errors-high`

**Database Connections Alarm:**
1. Create alarm:
   - **Metric**: RDS → DatabaseConnections
   - **Threshold**: Greater than 80
   - **Period**: 5 minutes
   - **Notification**: `govt-services-alerts`
   - **Name**: `database-connections-high`

### Step 6.3: Create CloudWatch Dashboard

1. Go to **CloudWatch** → **Dashboards** → **Create dashboard**
2. **Name**: `govt-services-prod`
3. Add widgets:
   - **ECS CPU/Memory**: Line graph with ECS metrics
   - **ALB Requests**: Line graph with request count
   - **RDS Metrics**: Line graph with DB connections, CPU
   - **Recent Errors**: Log query widget for error logs
4. Save dashboard

---

## Phase 7: Set Up CI/CD (Optional)

### Step 7.1: Configure GitHub Secrets

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `GEMINI_API_KEY`

### Step 7.2: Update GitHub Actions Workflows

The workflows are already created in `.github/workflows/`. They will automatically deploy when you push to main branch.

---

## Summary

You now have:
- ✅ VPC with public and private subnets
- ✅ RDS PostgreSQL database
- ✅ ECS Fargate running your backend
- ✅ Application Load Balancer
- ✅ S3 + CloudFront for frontend
- ✅ CloudWatch monitoring and alarms
- ✅ Automated deployments via GitHub Actions

## Access URLs

- **Backend API**: `http://YOUR_ALB_DNS`
- **Frontend**: `https://YOUR_CLOUDFRONT_DOMAIN`
- **Dashboard**: CloudWatch → Dashboards → `govt-services-prod`

## Estimated Monthly Cost

- **RDS db.t3.micro**: Free tier (first 12 months)
- **ECS Fargate**: ~$10-15/month
- **ALB**: ~$16/month
- **S3 + CloudFront**: ~$1-5/month
- **Total**: ~$27-36/month (after free tier)

## Next Steps

1. Set up custom domain (Route 53)
2. Add SSL certificate (ACM)
3. Configure auto-scaling
4. Set up database backups
5. Implement monitoring dashboards

Need help with any step? Let me know!
