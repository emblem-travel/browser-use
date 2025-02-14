#!/bin/bash
set -e
dnf update -y
dnf install -y docker wget
systemctl start docker
systemctl enable docker
mkdir -p /etc/app
aws s3 cp s3://${env_file_bucket}/${env_file_key} /etc/app/environment
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/arm64/latest/amazon-cloudwatch-agent.rpm
dnf install -y ./amazon-cloudwatch-agent.rpm
systemctl start amazon-cloudwatch-agent
systemctl enable amazon-cloudwatch-agent
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin ${ecr_repository_uri}
docker pull ${ecr_repository_uri}
docker run -d \
  --name ${app_name} \
  --restart always \
  --env-file /etc/app/environment \
  --log-driver=awslogs \
  --log-opt awslogs-region=us-east-2 \
  --log-opt awslogs-group="/aws/ec2/${app_name}" \
  --log-opt awslogs-stream="${app_name}-${environment}" \
  ${ecr_repository_uri}

