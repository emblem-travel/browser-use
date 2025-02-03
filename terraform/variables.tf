variable "vpc_id" {
  description = "ID of the existing VPC"
  type        = string
  default     = "vpc-0fb3c875f3eed4edb"
}

variable "private_subnet_id" {
  description = "ID of the private subnet"
  type        = string
  default     = "subnet-0f94c4e39b56732c6"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "emblem-browser-use"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "ami_id" {
  description = "ID of the AMI to use for EC2 instances"
  type        = string
  default     = "ami-0db575de70f37f380"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.small"
}

variable "ecr_repository_uri" {
  description = "URI of the ECR repository"
  type        = string
  default     = "339713015370.dkr.ecr.us-east-2.amazonaws.com/emblem/browser-use:latest"
}

variable "env_file_bucket" {
  description = "Name of the S3 bucket containing the environment file"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]+[a-z0-9]$", var.env_file_bucket))
    error_message = "The bucket name must be a valid S3 bucket name."
  }
  default = "emblem-secret-configs"
}

variable "env_file_key" {
  description = "Path to the environment file in S3 bucket"
  type        = string
  default     = "computer_use_env"
}

variable "key_name" {
  description = "Name of the EC2 key pair for SSH access"
  type        = string
  validation {
    condition     = length(var.key_name) > 0
    error_message = "Key name cannot be empty."
  }
  default = "computer_use_key"
}


variable "sqs_queue_name" {
  type        = string
  description = "Name of the SQS queue to monitor"
  default     = "availability_requests" # Update with your actual queue name
}

variable "public_subnet_id" {
  type        = string
  description = "public subnet ID"
  default     = "subnet-091a0fc4faba8ea49"
}
