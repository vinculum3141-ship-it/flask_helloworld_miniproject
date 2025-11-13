#!/bin/bash
# Setup script for Ingress on Minikube
# This script enables nginx ingress controller and configures /etc/hosts for local development

set -e

echo "=========================================="
echo "Setting up Ingress for Minikube"
echo "=========================================="

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Error: Minikube is not running. Please start it with 'minikube start'"
    exit 1
fi

echo "✓ Minikube is running"

# Enable ingress addon
echo ""
echo "Enabling nginx ingress controller addon..."
minikube addons enable ingress

# Wait for ingress controller to be ready
echo ""
echo "Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

echo "✓ Ingress controller is ready"

# Get minikube IP
MINIKUBE_IP=$(minikube ip)
echo ""
echo "Minikube IP: $MINIKUBE_IP"

# Check if hello-flask.local is already in /etc/hosts
HOST_ENTRY="$MINIKUBE_IP hello-flask.local"
if grep -q "hello-flask.local" /etc/hosts 2>/dev/null; then
    echo ""
    echo "⚠️  Entry for hello-flask.local already exists in /etc/hosts"
    echo "Current entry:"
    grep "hello-flask.local" /etc/hosts
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old entry
        sudo sed -i '/hello-flask.local/d' /etc/hosts
        # Add new entry
        echo "$HOST_ENTRY" | sudo tee -a /etc/hosts > /dev/null
        echo "✓ Updated /etc/hosts"
    else
        echo "⊘ Skipped updating /etc/hosts"
    fi
else
    echo ""
    echo "Adding entry to /etc/hosts (requires sudo)..."
    echo "$HOST_ENTRY" | sudo tee -a /etc/hosts > /dev/null
    echo "✓ Added $HOST_ENTRY to /etc/hosts"
fi

echo ""
echo "=========================================="
echo "Ingress setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Deploy your application:"
echo "   kubectl apply -f k8s/deployment.yaml"
echo "   kubectl apply -f k8s/service.yaml"
echo "   kubectl apply -f k8s/ingress.yaml"
echo ""
echo "2. Wait for ingress to be ready:"
echo "   kubectl get ingress hello-flask-ingress -w"
echo ""
echo "3. Access your application at:"
echo "   http://hello-flask.local"
echo ""
echo "To check ingress status:"
echo "   kubectl describe ingress hello-flask-ingress"
echo ""
