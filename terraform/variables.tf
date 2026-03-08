# Input variables for Terraform configuration

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  type        = string
  description = "AWS region for resource deployment"
  default     = "us-east-1"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
  default     = "10.0.0.0/16"
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class (free tier: db.t3.micro)"
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  type        = number
  description = "Allocated storage for RDS in GB (free tier: up to 20GB)"
  default     = 20
}

variable "db_name" {
  type        = string
  description = "Database name"
  default     = "govt_services"
}

variable "alert_email" {
  type        = string
  description = "Email address for CloudWatch alerts"
}

variable "gemini_api_key" {
  type        = string
  description = "Gemini API key for backend service"
  sensitive   = true
}
