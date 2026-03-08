# Networking module outputs

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "alb_sg_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

output "ecs_sg_id" {
  description = "ECS tasks security group ID"
  value       = aws_security_group.ecs.id
}

output "database_sg_id" {
  description = "RDS database security group ID"
  value       = aws_security_group.database.id
}

output "elasticache_sg_id" {
  description = "ElastiCache security group ID"
  value       = aws_security_group.elasticache.id
}
