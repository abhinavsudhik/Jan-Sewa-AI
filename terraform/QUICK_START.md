# Quick Start Guide

Get your application deployed to AWS in 5 steps.

## 1. Configure Variables

Edit `environments/prod.tfvars`:

```hcl
alert_email    = "your-email@example.com"
gemini_api_key = "your-gemini-api-key"
```

## 2. Initialize and Deploy

```bash
# Initialize Terraform
terraform init

# Deploy infrastructure
terraform apply -var-file=environments/prod.tfvars
```

## 3. Build and Push Backend Image

```bash
# Get ECR URL
ECR_REPO=$(terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REPO

# Build and push
cd ../backend
docker build -t $ECR_REPO:latest -f Dockerfile.prod .
docker push $ECR_REPO:latest
```

## 4. Deploy Frontend

```bash
cd ../frontend

# Build
BACKEND_URL=$(cd ../terraform && terraform output -raw backend_url)
NEXT_PUBLIC_API_URL=http://$BACKEND_URL npm run build

# Deploy to S3
BUCKET=$(cd ../terraform && terraform output -raw frontend_bucket_name)
aws s3 sync out/ s3://$BUCKET/ --delete

# Invalidate cache
DIST_ID=$(cd ../terraform && terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

## 5. Access Your Application

```bash
# Get URLs
cd terraform
echo "Backend: http://$(terraform output -raw backend_url)"
echo "Frontend: https://$(terraform output -raw frontend_url)"
```

## Set Up CI/CD

Add GitHub Secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Then push to `main` branch - deployments are automatic!

## Monitor

View dashboard: AWS Console → CloudWatch → Dashboards → `govt-services-prod`

## Need Help?

See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed instructions.
