#!/bin/bash
# Deployment script for Kubernetes

set -e

echo "🚀 Deploying AI Voice Knowledge Assistant to Kubernetes..."

# Build Docker images
echo "🐳 Building Docker images..."
docker build -t ai-assistant-gateway:latest -f deployment/docker/Dockerfile.gateway .
docker build -t ai-assistant-frontend:latest -f deployment/docker/Dockerfile.frontend .

# Tag and push images (adjust registry as needed)
REGISTRY=${REGISTRY:-"your-registry"}

if [ "$REGISTRY" != "your-registry" ]; then
    echo "📤 Pushing images to registry..."
    docker tag ai-assistant-gateway:latest $REGISTRY/ai-assistant-gateway:latest
    docker tag ai-assistant-frontend:latest $REGISTRY/ai-assistant-frontend:latest
    docker push $REGISTRY/ai-assistant-gateway:latest
    docker push $REGISTRY/ai-assistant-frontend:latest
fi

# Apply Kubernetes manifests
echo "☸️  Applying Kubernetes manifests..."
kubectl apply -f deployment/k8s/namespace.yaml
kubectl apply -f deployment/k8s/secrets.yaml -n ai-assistant
kubectl apply -f deployment/k8s/redis-deployment.yaml -n ai-assistant
kubectl apply -f deployment/k8s/gateway-deployment.yaml -n ai-assistant
kubectl apply -f deployment/k8s/frontend-deployment.yaml -n ai-assistant

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/redis -n ai-assistant
kubectl wait --for=condition=available --timeout=300s deployment/ai-assistant-gateway -n ai-assistant
kubectl wait --for=condition=available --timeout=300s deployment/ai-assistant-frontend -n ai-assistant

echo "✅ Deployment complete!"
echo ""
echo "Access your services:"
kubectl get services -n ai-assistant
