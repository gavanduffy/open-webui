#!/bin/bash
set -e

image_name="open-webui-arm64"
container_name="openweb-test"
host_port=3000
container_port=8080

# Build image for arm64 platform
docker build --platform linux/arm64 -t "$image_name" .

# Stop and remove existing container if exists
docker stop "$container_name" >/dev/null 2>&1 || true
docker rm "$container_name" >/dev/null 2>&1 || true

# Run container
docker run -d -p "$host_port":"$container_port" \
    --add-host=host.docker.internal:host-gateway \
    -v "${image_name}:/app/backend/data" \
    --name "$container_name" \
    --restart always \
    "$image_name"

# Remove dangling images
docker image prune -f >/dev/null

echo "Container '$container_name' is up and running on port $host_port"
