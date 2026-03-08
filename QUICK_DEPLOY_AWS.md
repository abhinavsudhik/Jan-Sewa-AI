# Quick AWS Deployment with App Runner

Deploy to AWS in 30 minutes using App Runner (simpler than ECS).

## Prerequisites

- AWS Account
- AWS CLI installed: `brew install awscli`
- Docker installed

## Step 1: Configure AWS (2 minutes)

```bash
aws configure
# Enter your AWS credentials
```

## Step 2: Create Database (15 minutes)

```bash
# Create RDS database (this takes time)
aws rds create-db-instance \
  --db-instance-identifier govt-services-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_STRONG_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids default \
  --publicly-accessible \
  --backup-retention-period 7

# Wait for database to be available (10-15 min)
aws rds wait db-instance-available --db-instance-identifier govt-services-db

# Get database endpoint
aws rds describe-db-instances \
  --db-instance-identifier govt-services-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

## Step 3: Deploy Backend with App Runner (5 minutes)

```bash
# Build and push to ECR
aws ecr create-repository --repository-name govt-services-backend

# Get ECR URI
ECR_URI=$(aws ecr describe-repositories --repository-names govt-services-backend --query 'repositories[0].repositoryUri' --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URI

# Build and push
cd backend
docker build -t govt-services-backend -f Dockerfile.prod .
docker tag govt-services-backend:latest $ECR_URI:latest
docker push $ECR_URI:latest

# Create App Runner service
aws apprunner create-service \
  --service-name govt-services-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR_URI':latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "DATABASE_URL": "postgresql://admin:YOUR_PASSWORD@YOUR_DB_ENDPOINT:5432/postgres",
          "ENVIRONMENT": "production"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }'

# Get backend URL
aws apprunner describe-service \
  --service-arn YOUR_SERVICE_ARN \
  --query 'Service.ServiceUrl' \
  --output text
```

## Step 4: Deploy Frontend to S3 + CloudFront (8 minutes)

```bash
# Create S3 bucket
BUCKET_NAME="govt-services-frontend-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME

# Build frontend
cd ../frontend
NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_URL npm run build

# Upload to S3
aws s3 sync out/ s3://$BUCKET_NAME/ --acl public-read

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name $BUCKET_NAME.s3.amazonaws.com \
  --default-root-object index.html

# Get CloudFront URL from output
```

## Done! 🎉

Your app is deployed:
- Backend: https://YOUR_APP_RUNNER_URL
- Frontend: https://YOUR_CLOUDFRONT_URL

**Total time:** ~30 minutes  
**Cost:** ~$20-30/month
