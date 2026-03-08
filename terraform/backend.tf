# Terraform backend configuration for state management
# Note: S3 bucket and DynamoDB table must be created manually before using this backend

terraform {
  backend "s3" {
    bucket         = "govt-services-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    
    # Uncomment after creating the S3 bucket and DynamoDB table
    # To initialize:
    # 1. Comment out this entire backend block
    # 2. Run: terraform init
    # 3. Create S3 bucket and DynamoDB table manually or with separate Terraform config
    # 4. Uncomment this block
    # 5. Run: terraform init -migrate-state
  }
}

# Instructions for setting up remote state backend:
# 
# 1. Create S3 bucket for state storage:
#    aws s3api create-bucket --bucket govt-services-terraform-state --region us-east-1
#    aws s3api put-bucket-versioning --bucket govt-services-terraform-state --versioning-configuration Status=Enabled
#    aws s3api put-bucket-encryption --bucket govt-services-terraform-state --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
#
# 2. Create DynamoDB table for state locking:
#    aws dynamodb create-table --table-name terraform-state-lock --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1
