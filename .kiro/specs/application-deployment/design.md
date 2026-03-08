# Design Document: Application Deployment

## Overview

This design specifies a production-ready AWS deployment architecture for a full-stack application consisting of a Python FastAPI backend, PostgreSQL database, Redis cache, and Next.js frontend. The deployment leverages AWS free tier resources where possible, implements infrastructure-as-code using Terraform, automates deployments through GitHub Actions, and provides comprehensive monitoring through AWS CloudWatch.

The architecture follows AWS best practices for security, scalability, and cost optimization while targeting small/MVP scale workloads. The design emphasizes automation, reproducibility, and operational excellence through infrastructure-as-code and CI/CD pipelines.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet Users                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Route 53     │ (DNS)
                    │  (Optional)    │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  CloudFront    │ (CDN + SSL)
                    │  Distribution  │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐        ┌──────────────┐
        │   S3 Bucket   │        │  ALB/API GW  │
        │  (Frontend    │        │  (Backend)   │
        │   Static)     │        └──────┬───────┘
        └───────────────┘               │
                                        ▼
                              ┌──────────────────┐
                              │   ECS Fargate    │
                              │   or App Runner  │
                              │  (FastAPI App)   │
                              └────────┬─────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │                             │
                        ▼                             ▼
                ┌───────────────┐           ┌─────────────────┐
                │   RDS         │           │  ElastiCache    │
                │  PostgreSQL   │           │     Redis       │
                │  (Free Tier)  │           │  (Optional)     │
                └───────────────┘           └─────────────────┘
```

### Network Architecture

- **VPC**: Custom VPC with public and private subnets across 2 availability zones
- **Public Subnets**: Host load balancer and NAT gateway
- **Private Subnets**: Host ECS tasks, RDS database, and ElastiCache
- **Security Groups**: Restrict traffic between components with least-privilege rules
- **NAT Gateway**: Enables private subnet resources to access internet for updates

### Deployment Strategy

- **Blue-Green Deployment**: For zero-downtime updates to backend services
- **Rolling Updates**: For frontend static assets via CloudFront invalidation
- **Automated Rollback**: Health check failures trigger automatic rollback
- **Canary Releases**: Optional gradual traffic shifting for high-risk changes

## Components and Interfaces

### 1. Infrastructure-as-Code (Terraform)

**Purpose**: Define and provision all AWS resources in a reproducible manner

**Modules**:
- `networking`: VPC, subnets, security groups, NAT gateway
- `compute`: ECS cluster, task definitions, App Runner service
- `database`: RDS PostgreSQL instance with security configuration
- `cache`: ElastiCache Redis cluster (optional for free tier)
- `storage`: S3 buckets for frontend and application storage
- `cdn`: CloudFront distribution with SSL certificate
- `monitoring`: CloudWatch log groups, alarms, dashboards
- `iam`: IAM roles and policies for services

**Key Files**:
```
terraform/
├── main.tf                 # Root module
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── backend.tf              # Terraform state configuration
├── modules/
│   ├── networking/
│   ├── compute/
│   ├── database/
│   ├── storage/
│   ├── cdn/
│   └── monitoring/
└── environments/
    ├── dev.tfvars
    └── prod.tfvars
```

**Interface**:
```hcl
# Input Variables
variable "environment" {
  type = string
  description = "Environment name (dev, staging, prod)"
}

variable "aws_region" {
  type = string
  default = "us-east-1"
}

variable "db_instance_class" {
  type = string
  default = "db.t3.micro"  # Free tier eligible
}

# Outputs
output "backend_url" {
  value = aws_lb.backend.dns_name
}

output "frontend_url" {
  value = aws_cloudfront_distribution.frontend.domain_name
}

output "database_endpoint" {
  value = aws_db_instance.postgres.endpoint
  sensitive = true
}
```

### 2. Backend Deployment (FastAPI on ECS Fargate)

**Purpose**: Run the FastAPI application in a containerized, scalable environment

**Container Configuration**:
```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**ECS Task Definition**:
```json
{
  "family": "govt-services-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "${ECR_REPOSITORY_URL}:${IMAGE_TAG}",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "secrets": [
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "REDIS_URL", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "GEMINI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/govt-services-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

**Service Configuration**:
- **Desired Count**: 1 (free tier)
- **Auto-scaling**: Optional, scale up to 2 tasks based on CPU/memory
- **Load Balancer**: Application Load Balancer with health checks
- **Service Discovery**: AWS Cloud Map for internal service discovery

### 3. Database Deployment (RDS PostgreSQL)

**Purpose**: Provide managed PostgreSQL database with automated backups and high availability

**Configuration**:
```hcl
resource "aws_db_instance" "postgres" {
  identifier = "govt-services-db"
  
  # Free tier eligible
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20  # Free tier: up to 20GB
  storage_type         = "gp2"
  storage_encrypted    = true
  
  # Database configuration
  db_name  = "govt_services"
  username = "admin"
  password = random_password.db_password.result
  
  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.private.name
  vpc_security_group_ids = [aws_security_group.database.id]
  publicly_accessible    = false
  
  # Backup configuration
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  # High availability (optional, not free tier)
  multi_az = false
  
  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn
  
  # Deletion protection
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "govt-services-db-final-snapshot"
  
  tags = {
    Environment = var.environment
  }
}
```

**Initialization**:
- Database schema initialization via migration scripts
- Use Alembic for database migrations
- Run migrations as part of deployment pipeline

### 4. Frontend Deployment (Next.js on S3 + CloudFront)

**Purpose**: Serve Next.js application with global CDN distribution and SSL

**Build Configuration**:
```json
// frontend/package.json
{
  "scripts": {
    "build": "next build",
    "export": "next export",
    "deploy": "npm run build && npm run export"
  }
}
```

**S3 Bucket Configuration**:
```hcl
resource "aws_s3_bucket" "frontend" {
  bucket = "govt-services-frontend-${var.environment}"
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  
  index_document {
    suffix = "index.html"
  }
  
  error_document {
    key = "404.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

**CloudFront Distribution**:
```hcl
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"  # US, Canada, Europe
  
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3-frontend"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend.cloudfront_access_identity_path
    }
  }
  
  # Backend API origin
  origin {
    domain_name = aws_lb.backend.dns_name
    origin_id   = "ALB-backend"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-frontend"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }
  
  # API routes
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-backend"
    
    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Origin"]
      cookies {
        forward = "all"
      }
    }
    
    viewer_protocol_policy = "https-only"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
    # For custom domain:
    # acm_certificate_arn = aws_acm_certificate.frontend.arn
    # ssl_support_method  = "sni-only"
    # minimum_protocol_version = "TLSv1.2_2021"
  }
  
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }
}
```

### 5. Environment Configuration (AWS Secrets Manager)

**Purpose**: Securely store and manage application secrets and configuration

**Secrets Structure**:
```hcl
resource "aws_secretsmanager_secret" "backend_secrets" {
  name = "govt-services/backend/${var.environment}"
  description = "Backend application secrets"
  
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "backend_secrets" {
  secret_id = aws_secretsmanager_secret.backend_secrets.id
  secret_string = jsonencode({
    DATABASE_URL   = "postgresql://${aws_db_instance.postgres.username}:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}/govt_services"
    REDIS_URL      = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379"
    SECRET_KEY     = random_password.secret_key.result
    GEMINI_API_KEY = var.gemini_api_key
    CORS_ORIGINS   = jsonencode(["https://${aws_cloudfront_distribution.frontend.domain_name}"])
  })
}
```

**IAM Policy for ECS Task**:
```hcl
resource "aws_iam_role_policy" "ecs_secrets_access" {
  name = "ecs-secrets-access"
  role = aws_iam_role.ecs_task_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.backend_secrets.arn
        ]
      }
    ]
  })
}
```

### 6. CI/CD Pipeline (GitHub Actions)

**Purpose**: Automate build, test, and deployment processes

**Workflow Structure**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: govt-services-backend
  ECS_SERVICE: govt-services-backend
  ECS_CLUSTER: govt-services-cluster
  ECS_TASK_DEFINITION: .aws/task-definition.json

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run linter
        run: |
          cd frontend
          npm run lint
      
      - name: Build
        run: |
          cd frontend
          npm run build

  deploy-backend:
    needs: [test-backend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -f Dockerfile.prod .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT
      
      - name: Fill in the new image ID in the Amazon ECS task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ${{ env.ECS_TASK_DEFINITION }}
          container-name: backend
          image: ${{ steps.build-image.outputs.image }}
      
      - name: Deploy Amazon ECS task definition
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
      
      - name: Verify deployment
        run: |
          BACKEND_URL=$(aws elbv2 describe-load-balancers \
            --names govt-services-backend-alb \
            --query 'LoadBalancers[0].DNSName' \
            --output text)
          
          for i in {1..10}; do
            if curl -f "http://$BACKEND_URL/health"; then
              echo "Health check passed"
              exit 0
            fi
            echo "Waiting for service to be healthy..."
            sleep 10
          done
          
          echo "Health check failed"
          exit 1

  deploy-frontend:
    needs: [test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Get backend URL
        id: backend-url
        run: |
          BACKEND_URL=$(aws cloudformation describe-stacks \
            --stack-name govt-services-infrastructure \
            --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
            --output text)
          echo "url=$BACKEND_URL" >> $GITHUB_OUTPUT
      
      - name: Build frontend
        env:
          NEXT_PUBLIC_API_URL: ${{ steps.backend-url.outputs.url }}
        run: |
          cd frontend
          npm ci
          npm run build
          npm run export
      
      - name: Deploy to S3
        run: |
          aws s3 sync frontend/out/ s3://govt-services-frontend-prod/ --delete
      
      - name: Invalidate CloudFront cache
        run: |
          DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
            --stack-name govt-services-infrastructure \
            --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
            --output text)
          
          aws cloudfront create-invalidation \
            --distribution-id $DISTRIBUTION_ID \
            --paths "/*"

  rollback:
    needs: [deploy-backend, deploy-frontend]
    runs-on: ubuntu-latest
    if: failure()
    
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Rollback ECS service
        run: |
          # Get previous task definition
          PREVIOUS_TASK_DEF=$(aws ecs describe-services \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE }} \
            --query 'services[0].deployments[1].taskDefinition' \
            --output text)
          
          # Update service to previous task definition
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE }} \
            --task-definition $PREVIOUS_TASK_DEF \
            --force-new-deployment
```

### 7. Monitoring and Logging (CloudWatch)

**Purpose**: Provide comprehensive observability for application health and performance

**Log Groups**:
```hcl
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/govt-services-backend"
  retention_in_days = 7  # Free tier: 5GB storage
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/cloudfront/govt-services-frontend"
  retention_in_days = 7
  
  tags = {
    Environment = var.environment
  }
}
```

**Metrics and Alarms**:
```hcl
# Backend CPU utilization alarm
resource "aws_cloudwatch_metric_alarm" "backend_cpu_high" {
  alarm_name          = "backend-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.backend.name
  }
}

# Backend error rate alarm
resource "aws_cloudwatch_metric_alarm" "backend_errors" {
  alarm_name          = "backend-error-rate-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5XXError"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors backend 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    LoadBalancer = aws_lb.backend.arn_suffix
  }
}

# Database connections alarm
resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "database-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS connections"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.id
  }
}
```

**Dashboard**:
```hcl
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "govt-services-${var.environment}"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", {stat = "Average"}],
            [".", "MemoryUtilization", {stat = "Average"}]
          ]
          period = 300
          stat = "Average"
          region = var.aws_region
          title = "ECS Resource Utilization"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", {stat = "Sum"}],
            [".", "TargetResponseTime", {stat = "Average"}],
            [".", "HTTPCode_Target_5XX_Count", {stat = "Sum"}]
          ]
          period = 300
          region = var.aws_region
          title = "Backend API Metrics"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", {stat = "Average"}],
            [".", "DatabaseConnections", {stat = "Average"}],
            [".", "FreeStorageSpace", {stat = "Average"}]
          ]
          period = 300
          region = var.aws_region
          title = "Database Metrics"
        }
      },
      {
        type = "log"
        properties = {
          query = "SOURCE '/ecs/govt-services-backend' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20"
          region = var.aws_region
          title = "Recent Errors"
        }
      }
    ]
  })
}
```

## Data Models

### Infrastructure State

**Terraform State**:
- Stored in S3 bucket with versioning enabled
- DynamoDB table for state locking
- Encrypted at rest

```hcl
terraform {
  backend "s3" {
    bucket         = "govt-services-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### Deployment Metadata

**ECS Task Metadata**:
```json
{
  "taskArn": "arn:aws:ecs:us-east-1:123456789012:task/...",
  "family": "govt-services-backend",
  "revision": "5",
  "desiredStatus": "RUNNING",
  "knownStatus": "RUNNING",
  "containers": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/govt-services-backend:abc123",
      "imageDigest": "sha256:...",
      "createdAt": "2024-01-15T10:30:00Z",
      "startedAt": "2024-01-15T10:30:15Z",
      "health": {
        "status": "HEALTHY"
      }
    }
  ]
}
```

### Secrets Schema

```json
{
  "backend_secrets": {
    "DATABASE_URL": "postgresql://user:pass@host:5432/dbname",
    "REDIS_URL": "redis://host:6379",
    "SECRET_KEY": "random-secret-key",
    "GEMINI_API_KEY": "api-key",
    "CORS_ORIGINS": "[\"https://example.com\"]"
  }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Infrastructure Provisioning Properties

Property 1: Infrastructure completeness
*For any* infrastructure configuration applied, all required AWS resources (VPC, subnets, security groups, compute services, database, storage) should be created and accessible
**Validates: Requirements 1.1, 1.2, 2.2, 3.1, 4.2**

Property 2: Free tier compliance
*For any* provisioned AWS resource, the instance types, storage sizes, and configurations should match AWS free tier specifications where applicable (db.t3.micro for RDS, 20GB storage, etc.)
**Validates: Requirements 1.3, 3.2, 11.1, 11.3**

Property 3: Infrastructure outputs
*For any* successful infrastructure provisioning, terraform outputs should contain all required connection endpoints and resource identifiers (backend URL, database endpoint, CloudFront domain, etc.)
**Validates: Requirements 1.4**

### Backend Deployment Properties

Property 4: Backend service health
*For any* deployed backend service, the /health endpoint should be accessible and return a successful status response
**Validates: Requirements 2.4**

Property 5: Environment variable injection
*For any* deployed service (backend or frontend), all required environment variables from secrets manager should be accessible to the running application
**Validates: Requirements 2.3, 5.2**

Property 6: Backend database connectivity
*For any* deployed backend service, the application should successfully connect to the RDS database using credentials from secrets manager
**Validates: Requirements 2.6**

Property 7: Load balancer routing
*For any* HTTP request to the backend service, traffic should be routed through the Application Load Balancer before reaching the ECS tasks
**Validates: Requirements 2.5**

Property 8: Backend dependency packaging
*For any* backend Docker image build, all dependencies listed in requirements.txt should be installed and importable in the container
**Validates: Requirements 2.1**

### Database Deployment Properties

Property 9: Database network isolation
*For any* deployed RDS instance, the database should be in a private subnet with no public IP address and only accessible from the backend security group
**Validates: Requirements 3.4, 3.6**

Property 10: Database backup configuration
*For any* deployed RDS instance, automated backups should be enabled with a retention period of at least 7 days
**Validates: Requirements 3.3, 10.1, 10.2**

Property 11: Database encryption
*For any* deployed RDS instance, encryption at rest should be enabled
**Validates: Requirements 9.2**

Property 12: Database credentials security
*For any* database deployment, credentials should be stored in AWS Secrets Manager and never appear in logs, code, or version control
**Validates: Requirements 3.5, 5.1, 5.5**

### Frontend Deployment Properties

Property 13: Frontend HTTPS accessibility
*For any* deployed frontend, the CloudFront distribution should be accessible via HTTPS with a valid SSL certificate and HTTP requests should redirect to HTTPS
**Validates: Requirements 4.5, 7.4**

Property 14: Frontend build optimization
*For any* frontend build, the Next.js production build should generate optimized static assets with minification and code splitting
**Validates: Requirements 4.1**

Property 15: Frontend API configuration
*For any* built frontend application, the backend API endpoint URL should be correctly injected as an environment variable and accessible in the application
**Validates: Requirements 4.4**

Property 16: CloudFront cache behavior
*For any* CloudFront distribution, static assets (/, /*, /_next/*) should have caching enabled while API routes (/api/*) should have caching disabled
**Validates: Requirements 4.6**

Property 17: S3 static asset deployment
*For any* frontend deployment, all built static assets should be uploaded to the S3 bucket and accessible through CloudFront
**Validates: Requirements 4.2**

### Environment Configuration Properties

Property 18: Secrets storage
*For any* sensitive credential (database password, API keys, secret keys), the value should be stored in AWS Secrets Manager or Parameter Store, not in code or environment files
**Validates: Requirements 5.1**

Property 19: Multi-environment separation
*For any* environment (dev, staging, prod), separate secret stores or parameter namespaces should exist with environment-specific configurations
**Validates: Requirements 5.3**

Property 20: Environment variable validation
*For any* service startup, if required environment variables are missing, the service should fail to start with a clear error message
**Validates: Requirements 5.6**

Property 21: Secret rotation support
*For any* secret update in Secrets Manager, restarting the service should load the new secret value
**Validates: Requirements 5.4**

### CI/CD Pipeline Properties

Property 22: Test-before-deploy
*For any* CI/CD pipeline execution, automated tests should run and pass before deployment steps execute
**Validates: Requirements 6.2**

Property 23: Test failure halts deployment
*For any* CI/CD pipeline execution where tests fail, deployment steps should not execute and developers should be notified
**Validates: Requirements 6.3**

Property 24: Docker image publishing
*For any* successful backend build, a Docker image should be pushed to Amazon ECR with a unique tag
**Validates: Requirements 6.4**

Property 25: Frontend asset deployment
*For any* successful frontend build, static assets should be uploaded to S3 and CloudFront cache should be invalidated
**Validates: Requirements 6.5**

Property 26: Post-deployment health verification
*For any* completed deployment, the CI/CD pipeline should verify service health by calling health check endpoints
**Validates: Requirements 6.6**

Property 27: Secure credential usage
*For any* CI/CD pipeline execution, AWS credentials should be loaded from GitHub Secrets, not hardcoded in workflow files
**Validates: Requirements 6.7**

### SSL and Security Properties

Property 28: SSL certificate provisioning
*For any* deployment, an SSL certificate should be provisioned through AWS Certificate Manager and attached to CloudFront and load balancers
**Validates: Requirements 7.1, 7.3**

Property 29: Security group least privilege
*For any* security group, ingress rules should only allow traffic from specific sources required for functionality (e.g., ALB to ECS, ECS to RDS)
**Validates: Requirements 9.1**

Property 30: Encryption in transit
*For any* service-to-service communication, connections should use TLS/HTTPS encryption
**Validates: Requirements 9.3**

Property 31: Private networking
*For any* backend-to-database or backend-to-cache communication, traffic should flow through private subnets without traversing the public internet
**Validates: Requirements 9.4**

Property 32: IAM least privilege
*For any* IAM role, the attached policies should grant only the minimum permissions required for the service to function
**Validates: Requirements 9.5**

Property 33: Audit logging
*For any* infrastructure change, AWS CloudTrail should log the event with timestamp, user, and action details
**Validates: Requirements 9.6**

Property 34: CORS restriction
*For any* backend API request, CORS headers should restrict allowed origins to the CloudFront frontend domain
**Validates: Requirements 9.7**

### Monitoring and Logging Properties

Property 35: Log collection
*For any* backend or frontend service, application logs should be collected and stored in CloudWatch Logs
**Validates: Requirements 8.1**

Property 36: Log retention
*For any* CloudWatch log group, a retention period should be configured (7 days for free tier optimization)
**Validates: Requirements 8.2**

Property 37: Health degradation alerts
*For any* service health degradation (high CPU, high error rate, database connection issues), CloudWatch alarms should trigger and send notifications via SNS
**Validates: Requirements 8.3**

Property 38: Metrics availability
*For any* deployed service, key metrics (request count, error rate, response time, CPU, memory) should be available in CloudWatch
**Validates: Requirements 8.4, 8.7**

Property 39: Dashboard visibility
*For any* deployment, a CloudWatch dashboard should exist displaying application performance and health metrics
**Validates: Requirements 8.5**

Property 40: Error logging detail
*For any* application error, the log entry should include stack trace, error message, and contextual information
**Validates: Requirements 8.6**

Property 41: Health check configuration
*For any* deployed service, automated health checks should be configured in ECS task definitions and load balancer target groups
**Validates: Requirements 8.8**

### Backup and Recovery Properties

Property 42: Point-in-time recovery
*For any* RDS instance with critical data, point-in-time recovery should be enabled allowing restoration to any point within the backup retention period
**Validates: Requirements 10.5**

### Cost Optimization Properties

Property 43: Auto-scaling configuration
*For any* ECS service, auto-scaling policies should be configured to scale down during low traffic periods
**Validates: Requirements 11.2**

Property 44: Cost monitoring
*For any* AWS account, CloudWatch billing alarms should be configured to alert on unexpected cost increases
**Validates: Requirements 11.4**

Property 45: S3 lifecycle policies
*For any* S3 bucket storing application data, lifecycle policies should be configured to transition or delete old objects
**Validates: Requirements 11.5**

### Rollback Properties

Property 46: Automatic rollback on health check failure
*For any* deployment where post-deployment health checks fail, the CI/CD pipeline should automatically rollback to the previous task definition
**Validates: Requirements 12.1**

Property 47: Version retention for rollback
*For any* deployment, at least the last 3 versions should be retained in ECR and ECS task definition history
**Validates: Requirements 12.2**

Property 48: Manual rollback capability
*For any* deployment, a manual rollback mechanism should be available through GitHub Actions workflow dispatch
**Validates: Requirements 12.3**

Property 49: Rollback logging
*For any* rollback event, the monitoring system should log the event with timestamp, reason, and version information
**Validates: Requirements 12.4**

Property 50: Post-rollback verification
*For any* completed rollback, health checks should verify the service is functioning correctly
**Validates: Requirements 12.5**

## Error Handling

### Infrastructure Provisioning Errors

**Terraform Apply Failures**:
- **Cause**: Resource limits, permission issues, invalid configuration
- **Handling**: Terraform will output detailed error messages indicating which resource failed and why
- **Recovery**: Fix configuration issues and re-apply; Terraform state ensures idempotency
- **Prevention**: Use `terraform plan` before apply; validate configurations in CI/CD

**Resource Creation Timeouts**:
- **Cause**: AWS service delays, network issues
- **Handling**: Terraform will retry with exponential backoff
- **Recovery**: Re-run terraform apply; existing resources won't be duplicated
- **Prevention**: Set appropriate timeout values in resource configurations

### Deployment Errors

**Docker Build Failures**:
- **Cause**: Missing dependencies, syntax errors, network issues
- **Handling**: CI/CD pipeline will fail at build step with error logs
- **Recovery**: Fix code issues and push new commit to trigger rebuild
- **Prevention**: Test builds locally; use multi-stage builds for efficiency

**ECS Task Launch Failures**:
- **Cause**: Insufficient resources, invalid task definition, missing secrets
- **Handling**: ECS will log failure reason in CloudWatch; service will not update
- **Recovery**: Fix task definition or resource allocation; redeploy
- **Prevention**: Validate task definitions; ensure secrets exist before deployment

**Health Check Failures**:
- **Cause**: Application errors, database connectivity issues, slow startup
- **Handling**: Load balancer will not route traffic to unhealthy tasks; automatic rollback triggered
- **Recovery**: Investigate logs; fix application issues; redeploy
- **Prevention**: Implement robust health checks; ensure adequate startup time

### Database Errors

**Connection Pool Exhaustion**:
- **Cause**: Too many concurrent connections, connection leaks
- **Handling**: Application will receive connection timeout errors
- **Recovery**: Restart application to reset connection pool; investigate connection leaks
- **Prevention**: Configure appropriate pool size; implement connection timeout; monitor connection metrics

**Database Migration Failures**:
- **Cause**: Schema conflicts, data integrity issues
- **Handling**: Migration script will fail with error message; database remains in previous state
- **Recovery**: Fix migration script; rollback if necessary; re-run migration
- **Prevention**: Test migrations in staging; use transaction-based migrations; maintain rollback scripts

**Storage Space Exhaustion**:
- **Cause**: Rapid data growth, insufficient initial allocation
- **Handling**: RDS will trigger CloudWatch alarm; database may become read-only
- **Recovery**: Increase allocated storage through AWS console or Terraform
- **Prevention**: Monitor storage metrics; set up alarms for 80% usage; implement data retention policies

### CI/CD Pipeline Errors

**Test Failures**:
- **Cause**: Code bugs, environment issues, flaky tests
- **Handling**: Pipeline halts at test stage; no deployment occurs
- **Recovery**: Fix failing tests; push new commit
- **Prevention**: Write reliable tests; use test retries for flaky tests; maintain test environment parity

**Deployment Timeout**:
- **Cause**: Slow application startup, resource constraints
- **Handling**: GitHub Actions workflow will timeout after configured duration
- **Recovery**: Investigate slow startup; increase timeout if legitimate; optimize application
- **Prevention**: Set realistic timeout values; monitor deployment duration trends

**Rollback Failures**:
- **Cause**: Previous version no longer available, infrastructure changes
- **Handling**: Manual intervention required; alert sent to operations team
- **Recovery**: Manually deploy known good version; investigate root cause
- **Prevention**: Maintain version history; test rollback procedures regularly

### Monitoring and Alerting Errors

**Missing Metrics**:
- **Cause**: Service not sending metrics, CloudWatch agent issues
- **Handling**: Monitoring dashboard will show gaps; alerts may not trigger
- **Recovery**: Restart services; verify CloudWatch agent configuration
- **Prevention**: Implement metric validation; alert on missing metrics

**Alert Fatigue**:
- **Cause**: Overly sensitive thresholds, transient issues
- **Handling**: Operations team may miss critical alerts
- **Recovery**: Tune alert thresholds; implement alert aggregation
- **Prevention**: Use appropriate evaluation periods; implement alert severity levels

## Testing Strategy

### Infrastructure Testing

**Terraform Validation**:
- Use `terraform validate` to check syntax and configuration
- Use `terraform plan` to preview changes before applying
- Implement automated validation in CI/CD pipeline

**Infrastructure Tests**:
- Use Terratest or similar framework to validate infrastructure
- Test resource creation, configuration, and connectivity
- Verify security group rules, IAM policies, and network configuration
- Run tests in isolated AWS account or use localstack for local testing

**Example Infrastructure Test**:
```go
// Test that RDS instance is created with correct configuration
func TestRDSInstance(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../terraform",
    }
    
    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)
    
    // Verify RDS instance exists
    dbInstanceID := terraform.Output(t, terraformOptions, "db_instance_id")
    assert.NotEmpty(t, dbInstanceID)
    
    // Verify instance class is free tier eligible
    instanceClass := aws.GetRDSInstanceClass(t, dbInstanceID, "us-east-1")
    assert.Equal(t, "db.t3.micro", instanceClass)
    
    // Verify encryption is enabled
    encrypted := aws.GetRDSInstanceEncryption(t, dbInstanceID, "us-east-1")
    assert.True(t, encrypted)
}
```

### Application Testing

**Backend Unit Tests**:
- Test individual FastAPI endpoints and business logic
- Mock external dependencies (database, Redis, external APIs)
- Use pytest with coverage reporting
- Run in CI/CD pipeline before deployment

**Backend Integration Tests**:
- Test with real database (use Docker Compose for local testing)
- Verify database migrations work correctly
- Test authentication and authorization flows
- Verify API contracts and response formats

**Frontend Unit Tests**:
- Test React components in isolation
- Mock API calls and external dependencies
- Use Jest and React Testing Library
- Run in CI/CD pipeline before deployment

**Frontend Integration Tests**:
- Test user flows with real API calls (against staging backend)
- Verify routing and navigation
- Test form submissions and data display
- Use Cypress or Playwright for end-to-end testing

### Property-Based Testing

**Infrastructure Properties**:
- **Property 1 (Infrastructure completeness)**: After applying terraform configuration, verify all required resources exist by querying AWS APIs
- **Property 2 (Free tier compliance)**: For all provisioned resources, verify instance types and configurations match free tier specifications
- **Property 9 (Database network isolation)**: For any RDS instance, verify it has no public IP and security groups only allow backend access

**Deployment Properties**:
- **Property 4 (Backend service health)**: For any deployed backend, repeatedly call /health endpoint and verify 200 response
- **Property 13 (Frontend HTTPS accessibility)**: For any frontend URL, verify HTTPS works and HTTP redirects to HTTPS
- **Property 22 (Test-before-deploy)**: For any CI/CD run, verify test jobs complete before deploy jobs start

**Security Properties**:
- **Property 12 (Database credentials security)**: For any deployment, scan logs and code for database credentials; verify none found
- **Property 29 (Security group least privilege)**: For any security group, verify ingress rules only allow required sources
- **Property 34 (CORS restriction)**: For any API request with invalid origin, verify CORS error is returned

**Configuration**:
- Minimum 100 iterations per property test
- Tag each test with: **Feature: application-deployment, Property {number}: {property_text}**
- Use appropriate property-based testing library (Hypothesis for Python, fast-check for TypeScript)

### Deployment Testing

**Smoke Tests**:
- After each deployment, run automated smoke tests
- Verify critical endpoints are accessible
- Check database connectivity
- Verify frontend loads and displays data

**Canary Deployment Testing**:
- Deploy to small percentage of traffic first
- Monitor error rates and performance metrics
- Gradually increase traffic if metrics are healthy
- Automatic rollback if error rate exceeds threshold

**Rollback Testing**:
- Periodically test rollback procedures in staging
- Verify rollback completes within acceptable time
- Verify service health after rollback
- Document rollback procedures and keep updated

### Monitoring and Observability Testing

**Alert Testing**:
- Trigger test alerts to verify notification delivery
- Test alert escalation procedures
- Verify alert thresholds are appropriate
- Test on-call rotation and incident response

**Dashboard Testing**:
- Verify all metrics are displayed correctly
- Test dashboard refresh and time range selection
- Ensure dashboards are accessible to operations team
- Document dashboard usage and interpretation

### Performance Testing

**Load Testing**:
- Use tools like Locust or k6 to simulate traffic
- Test backend API endpoints under load
- Verify auto-scaling triggers at appropriate thresholds
- Identify performance bottlenecks

**Stress Testing**:
- Test system behavior under extreme load
- Verify graceful degradation
- Test recovery after stress period
- Identify breaking points and resource limits

### Security Testing

**Vulnerability Scanning**:
- Scan Docker images for known vulnerabilities (Trivy, Snyk)
- Run security linters on infrastructure code (tfsec, checkov)
- Scan dependencies for security issues
- Integrate scanning into CI/CD pipeline

**Penetration Testing**:
- Test authentication and authorization
- Verify input validation and sanitization
- Test for common vulnerabilities (SQL injection, XSS, CSRF)
- Conduct periodic security audits

**Compliance Testing**:
- Verify encryption at rest and in transit
- Test access controls and IAM policies
- Verify audit logging is enabled
- Test backup and recovery procedures

### Testing Balance

This deployment spec emphasizes infrastructure validation and integration testing over extensive unit testing. The focus is on:

1. **Infrastructure correctness**: Verify resources are created with correct configurations
2. **Integration points**: Test service-to-service communication and external dependencies
3. **Security validation**: Verify security controls are properly configured
4. **Deployment automation**: Test CI/CD pipeline and rollback procedures
5. **Operational readiness**: Verify monitoring, logging, and alerting work correctly

Property-based tests validate universal properties across all deployments, while integration tests verify specific deployment scenarios. Together, they provide comprehensive coverage of deployment correctness and operational requirements.
