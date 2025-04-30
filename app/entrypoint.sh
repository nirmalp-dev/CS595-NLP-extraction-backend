#!/bin/sh
set -e

# Start MinIO server in the background
/minio server /data --console-address ":9001" &

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
until mc alias set myminio http://localhost:9000 minio minio123 2>/dev/null; do
  sleep 2
done

# Create the bucket if it doesn't exist
mc mb myminio/uploads || true

# Add the webhook event notification for object creation (PUT)
mc event add myminio/uploads arn:minio:sqs::primary:webhook --event put || true

echo "MinIO setup complete. Bringing server to foreground..."
wait
