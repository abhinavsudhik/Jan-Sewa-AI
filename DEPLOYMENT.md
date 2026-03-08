# Deployment Guide

This guide will help you deploy the Government Services application to AWS using the infrastructure-as-code setup.

## Prerequisites

Before you begin, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Terraform** >= 1.0 installed
4. **GitHub repository** with the code
5. **Domain name** (optional, for custom domain)

## Step 1: Set Up AWS Credentials

Configure your AWS credentials locally:

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)

## Step 2: Configure Terraform Backend (Optional but Recommended)

For production deployments, set up remote state storage:

```bash
# Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket govt-services-terraform-state \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket govt-services-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket govt-services-terraform-state \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

Then uncomment the backend configuration in `terraform/backend.tf`.

## Step 3: Configure Environment Variables

Edit `terraform/environments/prod.tfvars`:

```hcl
environment           = "prod"
aws_region            = "us-east-1"
vpc_cidr              = "10.0.0.0/16"
db_instance_class     = "db.t3.micro"
db_allocated_storage  = 20
db_name               = "govt_services"
alert_email           = "your-email@example.com"  # Change this
gemini_api_key        = "your-gemini-api-key"     # Change this
```

## Step 4: Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan -var-file=environments/prod.tfvars

# Apply the configuration
terraform apply -var-file=environments/prod.tfvars
```

This will create:
- VPC with public and private subnets
- RDS PostgreSQL database
- ECS Fargate cluster
- Application Load Balancer
- S3 bucket for frontend
- CloudFront distribution
- CloudWatch monitoring and alarms
- ECR repository for Docker images

**Note:** The initial deployment takes 10-15 minutes.

## Step 5: Save Terraform Outputs

After deployment, save the outputs:

```bash
terraform output > ../deployment-outputs.txt
```

Important outputs:
- `backend_url`: ALB DNS name for backend API
- `frontend_url`: CloudFront domain for frontend
- `ecr_repository_url`: ECR repository for Docker images
- `frontend_bucket_name`: S3 bucket name

## Step 6: Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. `AWS_ACCESS_KEY_ID`: Your AWS access key
2. `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
3. `GEMINI_API_KEY`: Your Gemini API key (if not already in Terraform)

## Step 7: Build and Push Initial Backend Image

```bash
# Get ECR repository URL from Terraform outputs
ECR_REPO=$(cd terraform && terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Build and push backend image
cd backend
docker build -t $ECR_REPO:latest -f Dockerfile.prod .
docker push $ECR_REPO:latest
```

## Step 8: Deploy Backend to ECS

The ECS service will automatically pull the latest image from ECR. Wait a few minutes for the service to start.

Check the service status:

```bash
aws ecs describe-services \
  --cluster govt-services-cluster-prod \
  --services govt-services-backend-prod \
  --query 'services[0].deployments'
```

## Step 9: Deploy Frontend to S3

```bash
cd frontend

# Get backend URL
BACKEND_URL=$(cd ../terraform && terraform output -raw backend_url)

# Build frontend with backend URL
NEXT_PUBLIC_API_URL=http://$BACKEND_URL npm run build

# Deploy to S3
BUCKET_NAME=$(cd ../terraform && terraform output -raw frontend_bucket_name)
aws s3 sync out/ s3://$BUCKET_NAME/ --delete

# Invalidate CloudFront cache
DISTRIBUTION_ID=$(cd ../terraform && terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

## Step 10: Verify Deployment

1. **Backend Health Check:**
   ```bash
   BACKEND_URL=$(cd terraform && terraform output -raw backend_url)
   curl http://$BACKEND_URL/health
   ```

2. **Frontend Access:**
   ```bash
   FRONTEND_URL=$(cd terraform && terraform output -raw frontend_url)
   echo "Frontend: https://$FRONTEND_URL"
   ```

3. **Check CloudWatch Logs:**
   - Go to AWS Console → CloudWatch → Log groups
   - Check `/ecs/govt-services-backend-prod` for backend logs

4. **View Monitoring Dashboard:**
   - Go to AWS Console → CloudWatch → Dashboards
   - Open `govt-services-prod` dashboard

## Automated Deployments (CI/CD)

Once GitHub secrets are configured, deployments are automatic:

- **Backend:** Push to `main` branch with changes in `backend/` triggers deployment
- **Frontend:** Push to `main` branch with changes in `frontend/` triggers deployment

Monitor deployments in GitHub Actions tab.

## Rollback

If a deployment fails, the GitHub Actions workflow will automatically rollback to the previous version.

For manual rollback:

```bash
# Get previous task definition
PREVIOUS_TASK=$(aws ecs describe-services \
  --cluster govt-services-cluster-prod \
  --services govt-services-backend-prod \
  --query 'services[0].deployments[1].taskDefinition' \
  --output text)

# Rollback
aws ecs update-service \
  --cluster govt-services-cluster-prod \
  --service govt-services-backend-prod \
  --task-definition $PREVIOUS_TASK \
  --force-new-deployment
```

## Cost Optimization

The deployment uses AWS free tier resources where possible:

- **RDS:** db.t3.micro (free tier eligible)
- **ECS Fargate:** 256 CPU / 512 MB memory (minimal cost)
- **S3:** Pay per GB stored and transferred
- **CloudFront:** Free tier includes 1TB data transfer
- **CloudWatch:** Free tier includes 5GB logs

**Estimated monthly cost:** $10-30 for small/MVP workloads

Set up billing alerts in AWS Console to monitor costs.

## Troubleshooting

### Backend not starting
- Check ECS task logs in CloudWatch
- Verify secrets are correctly configured in Secrets Manager
- Check security group rules allow ALB → ECS traffic

### Frontend not loading
- Verify S3 bucket has files: `aws s3 ls s3://govt-services-frontend-prod/`
- Check CloudFront distribution status
- Verify CloudFront origin is pointing to correct S3 bucket

### Database connection issues
- Verify RDS instance is running
- Check security group allows ECS → RDS traffic on port 5432
- Verify DATABASE_URL in Secrets Manager is correct

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy -var-file=environments/prod.tfvars
```

**Warning:** This will delete all resources including the database. Ensure you have backups before destroying.

## Support

For issues or questions:
1. Check CloudWatch logs for error messages
2. Review GitHub Actions workflow logs
3. Check AWS Console for resource status
4. Review Terraform plan output for configuration issues
