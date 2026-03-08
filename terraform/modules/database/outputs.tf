# Database module outputs

output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.postgres.id
}

output "db_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.postgres.db_name
}

output "backend_secrets_arn" {
  description = "ARN of backend secrets in Secrets Manager"
  value       = aws_secretsmanager_secret.backend_secrets.arn
}
