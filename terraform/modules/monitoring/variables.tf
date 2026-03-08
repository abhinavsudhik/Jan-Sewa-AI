# Monitoring module variables

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "ecs_cluster_name" {
  type        = string
  description = "ECS cluster name"
}

variable "ecs_service_name" {
  type        = string
  description = "ECS service name"
}

variable "alb_arn_suffix" {
  type        = string
  description = "ALB ARN suffix for CloudWatch metrics"
}

variable "db_instance_id" {
  type        = string
  description = "RDS instance ID"
}

variable "alert_email" {
  type        = string
  description = "Email address for CloudWatch alerts"
}
