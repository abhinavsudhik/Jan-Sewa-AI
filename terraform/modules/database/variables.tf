# Database module variables

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs for RDS"
}

variable "database_sg_id" {
  type        = string
  description = "Security group ID for RDS"
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class"
}

variable "db_allocated_storage" {
  type        = number
  description = "Allocated storage in GB"
}

variable "db_name" {
  type        = string
  description = "Database name"
}
