provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_iam_role" "execution_role" {
  name = "fargate_execution_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
    
  ]
}
EOF 
}


resource "aws_iam_policy" "s3_write_policy" {
  name        = "s3-write-policy"
  description = "Allow S3 write access"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action   = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      Effect   = "Allow",
      Resource = [
        "arn:aws:s3:::bayesian-soccer-traces-matthew-burke/*",  # Replace with your S3 bucket ARN
        "arn:aws:s3:::bayesian-soccer-traces-matthew-burke"       # Replace with your S3 bucket ARN
      ]
    }]
  })
}



resource "aws_iam_role_policy_attachment" "execution_role_policy" {
  role       = aws_iam_role.execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "execution_role_policy_s3" {
  role       = aws_iam_role.execution_role.name
  policy_arn = aws_iam_policy.s3_write_policy.arn 
}

resource "aws_iam_role" "ecs_task_role" {
  name = "ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "s3_write_attachment" {
  policy_arn = aws_iam_policy.s3_write_policy.arn
  role       = aws_iam_role.ecs_task_role.name
}


resource "aws_ecs_task_definition" "fargate_task" {
  family                   = "fargate_task_family"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn


  container_definitions = <<DEFINITION
[
  {
    "name": "fargate_task",
    "image": "812140451703.dkr.ecr.ap-southeast-2.amazonaws.com/mattsrepo:create-bayesian-trace",
    "essential": true,
    "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "bayeian-football",
            "awslogs-region": "ap-southeast-2",
            "awslogs-stream-prefix": "ecs"
          }
        }
  }
]
DEFINITION
}

resource "aws_ecs_cluster" "fargate_task" {
  name = "my-ecs-cluster"
}

resource "aws_cloudwatch_event_rule" "fargate_task" {
  name        = "fargate_task"
  description = "Schedule fargate task"
  is_enabled = true
  schedule_expression = "rate(7 days)"
}

resource "aws_cloudwatch_event_target" "fargate_task" {
  target_id = "fargate_task"
  arn       = aws_ecs_cluster.fargate_task.arn 
  rule      = aws_cloudwatch_event_rule.fargate_task.name
  role_arn  = aws_iam_role.execution_role.arn 

  # Contains the Amazon ECS task definition and task count to be used, if the event target is an Amazon ECS task.
  # https://docs.aws.amazon.com/AmazonCloudWatchEvents/latest/APIReference/API_EcsParameters.html
  ecs_target {
    launch_type         = "FARGATE"
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fargate_task.arn
    network_configuration {
      assign_public_ip = false

      subnets = [aws_subnet.private.arn]
    }
  }
}


resource "aws_vpc" "aws-vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = false
  enable_dns_support   = false
  tags = {
    Name        = "fargate_task-vpc"
    Environment = "farget_task"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.aws-vpc.id
  cidr_block = "10.0.0.0/16"

  tags = {
    Name        = "private_subnet"
    Environment = "fargate_task"
  }
}
