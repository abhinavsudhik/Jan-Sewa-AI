# Main Terraform configuration for application deployment
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "govt-services"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Networking module
module "networking" {
  source = "./modules/networking"
  
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

# Database module
module "database" {
  source = "./modules/database"
  
  environment           = var.environment
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  database_sg_id        = module.networking.database_sg_id
  db_instance_class     = var.db_instance_class
  db_allocated_storage  = var.db_allocated_storage
  db_name               = var.db_name
}

# Compute module
module "compute" {
  source = "./modules/compute"
  
  environment         = var.environment
  vpc_id              = module.networking.vpc_id
  public_subnet_ids   = module.networking.public_subnet_ids
  private_subnet_ids  = module.networking.private_subnet_ids
  ecs_sg_id           = module.networking.ecs_sg_id
  alb_sg_id           = module.networking.alb_sg_id
  backend_secrets_arn = module.database.backend_secrets_arn
}

# Storage module
module "storage" {
  source = "./modules/storage"
  
  environment = var.environment
}

# CDN module
module "cdn" {
  source = "./modules/cdn"
  
  environment        = var.environment
  frontend_bucket_id = module.storage.frontend_bucket_id
  frontend_bucket_regional_domain_name = module.storage.frontend_bucket_regional_domain_name
  alb_dns_name       = module.compute.alb_dns_name
}

# Monitoring module
module "monitoring" {
  source = "./modules/monitoring"
  
  environment       = var.environment
  ecs_cluster_name  = module.compute.ecs_cluster_name
  ecs_service_name  = module.compute.ecs_service_name
  alb_arn_suffix    = module.compute.alb_arn_suffix
  db_instance_id    = module.database.db_instance_id
  alert_email       = var.alert_email
}
