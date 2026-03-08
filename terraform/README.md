# Terraform Infrastructure

This directory contains Terraform configuration for deploying the application infrastructure to AWS.

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- AWS account with permissions to create VPC, ECS, RDS, S3, CloudFront, etc.

## Directory Structure

```
terraform/
├── main.tf              # Main configuration with module calls
├── variables.tf         # Input variable definitions
├── outputs.tf           # Output value definitions
├── backend.tf           # Remote state backend configuration
├── modules/             # Terraform modules
│   ├── networking/      # VPC, subnets, security groups
│   ├── compute/         # ECS, ECR, ALB
│   ├── database/        # RDS PostgreSQL
│   ├── storage/         # S3 buckets
│   ├── cdn/             # CloudFront distribution
│   └── monitoring/      # CloudWatch logs, alarms, dashboards
└── environments/        # Environment-specific variable files
    ├── dev.tfvars
    └── prod.tfvars
```

## Setup

### 1. Configure Backend (Optional)

For production use, set up remote state storage:

```bash
# Create S3 bucket for state
aws s3api create-bucket --bucket govt-services-terraform-state --region us-east-1
aws s3api put-bucket-versioning --bucket govt-services-terraform-state --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket govt-services-terraform-state --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

Then uncomment the backend configuration in `backend.tf` and run `terraform init -migrate-state`.

### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

### 3. Configure Variables

Edit the appropriate environment file (`environments/dev.tfvars` or `environments/prod.tfvars`) and set:
- `alert_email`: Your email for CloudWatch alerts
- `gemini_api_key`: Your Gemini API key

### 4. Plan Deployment

```bash
terraform plan -var-file=environments/dev.tfvars
```

### 5. Apply Configuration

```bash
terraform apply -var-file=environments/dev.tfvars
```

## Outputs

After successful deployment, Terraform will output:
- `backend_url`: ALB DNS name for backend API
- `frontend_url`: CloudFront domain for frontend
- `frontend_bucket_name`: S3 bucket for frontend assets
- `cloudfront_distribution_id`: For cache invalidation
- `ecr_repository_url`: For pushing Docker images
- `ecs_cluster_name` and `ecs_service_name`: For deployments

## Cleanup

To destroy all resources:

```bash
terraform destroy -var-file=environments/dev.tfvars
```

**Warning**: This will delete all resources including the database. Ensure you have backups before destroying.
