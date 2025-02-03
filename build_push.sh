docker buildx build \
    --platform linux/arm64 \
  -t 339713015370.dkr.ecr.us-east-2.amazonaws.com/emblem/browser-use:latest \
  --push \
  .