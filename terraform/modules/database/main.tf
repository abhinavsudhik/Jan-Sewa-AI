# Database module - RDS PostgreSQL

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# DB Subnet Group
resource "aws_db_subnet_group" "private" {
  name       = "govt-services-db-subnet-${var.environment}"
  subnet_ids = var.private_subnet_ids
  
  tags = {
    Name = "govt-services-db-subnet-${var.environment}"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier = "govt-services-db-${var.environment}"
  
  # Free tier eligible configuration
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  storage_type         = "gp2"
  storage_encrypted    = true
  
  # Database configuration
  db_name  = var.db_name
  username = "admin"
  password = random_password.db_password.result
  port     = 5432
  
  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.private.name
  vpc_security_group_ids = [var.database_sg_id]
  publicly_accessible    = false
  
  # Backup configuration
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  # High availability (disabled for free tier)
  multi_az = false
  
  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_monitoring.arn
  
  # Performance Insights (optional, may incur costs)
  performance_insights_enabled = false
  
  # Deletion protection
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "govt-services-db-final-snapshot-${var.environment}-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  
  # Point-in-time recovery
  copy_tags_to_snapshot = true
  
  tags = {
    Name = "govt-services-db-${var.environment}"
  }
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "govt-services-rds-monitoring-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name = "govt-services-rds-monitoring-${var.environment}"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}


# Secrets Manager for backend secrets
resource "random_password" "secret_key" {
  length  = 64
  special = true
}

resource "aws_secretsmanager_secret" "backend_secrets" {
  name                    = "govt-services/backend/${var.environment}"
  description             = "Backend application secrets"
  recovery_window_in_days = 7
  
  tags = {
    Name = "govt-services-backend-secrets-${var.environment}"
  }
}

resource "aws_secretsmanager_secret_version" "backend_secrets" {
  secret_id = aws_secretsmanager_secret.backend_secrets.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql://admin:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}/${var.db_name}"
    SECRET_KEY   = random_password.secret_key.result
    ENVIRONMENT  = var.environment
  })
}
