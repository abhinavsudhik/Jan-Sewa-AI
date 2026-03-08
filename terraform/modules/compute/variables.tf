# Compute module variables

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "List of public subnet IDs for ALB"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs for ECS tasks"
}

variable "ecs_sg_id" {
  type        = string
  description = "Security group ID for ECS tasks"
}

variable "alb_sg_id" {
  type        = string
  description = "Security group ID for ALB"
}

variable "backend_secrets_arn" {
  type        = string
  description = "ARN of backend secrets in Secrets Manager"
}
