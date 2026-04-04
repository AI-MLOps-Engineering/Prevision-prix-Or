#!/bin/bash

set -e

echo "[INFO] Installing Docker..."
apt update -y
apt install -y docker.io docker-compose-plugin

echo "[INFO] Starting Docker..."
systemctl enable docker
systemctl start docker

echo "[INFO] Running docker-compose..."
docker compose -f /root/docker-compose.yaml up -d --build

echo "[INFO] Deployment complete!"
