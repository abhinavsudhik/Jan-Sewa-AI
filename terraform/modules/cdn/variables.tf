# CDN module variables

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "frontend_bucket_id" {
  type        = string
  description = "Frontend S3 bucket ID"
}

variable "frontend_bucket_regional_domain_name" {
  type        = string
  description = "Frontend S3 bucket regional domain name"
}

variable "alb_dns_name" {
  type        = string
  description = "ALB DNS name for backend API"
}
