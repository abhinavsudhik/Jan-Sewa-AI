# Output values from Terraform deployment

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "backend_url" {
  description = "Backend Application Load Balancer DNS name"
  value       = module.compute.alb_dns_name
}

output "frontend_url" {
  description = "Frontend CloudFront distribution domain name"
  value       = module.cdn.cloudfront_domain_name
}

output "frontend_bucket_name" {
  description = "S3 bucket name for frontend static assets"
  value       = module.storage.frontend_bucket_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = module.cdn.cloudfront_distribution_id
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = module.database.db_endpoint
  sensitive   = true
}

output "ecr_repository_url" {
  description = "ECR repository URL for backend Docker images"
  value       = module.compute.ecr_repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.compute.ecs_cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.compute.ecs_service_name
}

output "backend_secrets_arn" {
  description = "ARN of backend secrets in Secrets Manager"
  value       = module.database.backend_secrets_arn
  sensitive   = true
}
