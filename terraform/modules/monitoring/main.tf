# Monitoring module - CloudWatch logs, alarms, dashboards

# CloudWatch Log Group for CloudFront (already created in compute module for backend)
resource "aws_cloudwatch_log_group" "cloudfront" {
  name              = "/cloudfront/govt-services-frontend-${var.environment}"
  retention_in_days = 7
  
  tags = {
    Name = "govt-services-cloudfront-logs-${var.environment}"
  }
}


# SNS Topic for alerts (will be created in next task)
resource "aws_sns_topic" "alerts" {
  name = "govt-services-alerts-${var.environment}"
  
  tags = {
    Name = "govt-services-alerts-${var.environment}"
  }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Backend CPU Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "backend_cpu_high" {
  alarm_name          = "govt-services-backend-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors ECS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }
  
  tags = {
    Name = "backend-cpu-high-${var.environment}"
  }
}

# Backend Memory Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "backend_memory_high" {
  alarm_name          = "govt-services-backend-memory-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors ECS memory utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }
  
  tags = {
    Name = "backend-memory-high-${var.environment}"
  }
}

# Backend 5XX Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "backend_errors" {
  alarm_name          = "govt-services-backend-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors backend 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"
  
  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }
  
  tags = {
    Name = "backend-errors-${var.environment}"
  }
}

# Database Connections Alarm
resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "govt-services-db-connections-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors RDS connections"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = var.db_instance_id
  }
  
  tags = {
    Name = "db-connections-high-${var.environment}"
  }
}

# Database CPU Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "govt-services-db-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = var.db_instance_id
  }
  
  tags = {
    Name = "db-cpu-high-${var.environment}"
  }
}

# Estimated Charges Alarm
resource "aws_cloudwatch_metric_alarm" "estimated_charges" {
  alarm_name          = "govt-services-estimated-charges-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600
  statistic           = "Maximum"
  threshold           = 10
  alarm_description   = "This metric monitors estimated AWS charges"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    Currency = "USD"
  }
  
  tags = {
    Name = "estimated-charges-${var.environment}"
  }
}


# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "govt-services-${var.environment}"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        x    = 0
        y    = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", { stat = "Average", label = "CPU" }],
            [".", "MemoryUtilization", { stat = "Average", label = "Memory" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "ECS Resource Utilization"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", { stat = "Sum", label = "Requests" }],
            [".", "TargetResponseTime", { stat = "Average", label = "Response Time (ms)", yAxis = "right" }],
            [".", "HTTPCode_Target_5XX_Count", { stat = "Sum", label = "5XX Errors" }]
          ]
          period = 300
          region = data.aws_region.current.name
          title  = "Backend API Metrics"
          yAxis = {
            left = {
              label = "Count"
            }
            right = {
              label = "Response Time (ms)"
            }
          }
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 6
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", { stat = "Average", label = "CPU %" }],
            [".", "DatabaseConnections", { stat = "Average", label = "Connections" }],
            [".", "FreeStorageSpace", { stat = "Average", label = "Free Storage (bytes)" }]
          ]
          period = 300
          region = data.aws_region.current.name
          title  = "Database Metrics"
        }
      },
      {
        type = "log"
        x    = 12
        y    = 6
        width = 12
        height = 6
        properties = {
          query   = "SOURCE '/ecs/govt-services-backend-${var.environment}' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20"
          region  = data.aws_region.current.name
          title   = "Recent Errors"
        }
      }
    ]
  })
}

data "aws_region" "current" {}
