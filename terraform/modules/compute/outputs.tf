# Compute module outputs

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.backend.name
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.backend.dns_name
}

output "alb_arn_suffix" {
  description = "ALB ARN suffix for CloudWatch metrics"
  value       = aws_lb.backend.arn_suffix
}

output "target_group_arn" {
  description = "Target group ARN"
  value       = aws_lb_target_group.backend.arn
}
