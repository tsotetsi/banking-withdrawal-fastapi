#!/bin/bash

echo "Starting Minikube..."
minikube start --memory=4096 --cpus=2

echo "Setting Docker to use Minikube's daemon..."
eval $(minikube docker-env)

echo "Building Docker image inside Minikube..."
docker build -t banking-api:latest .

echo "Cleaning up any previous deployment..."
kubectl delete -f k9s/ --ignore-not-found=true

echo "Setting up Kubernetes resources..."
kubectl apply -f k9s/namespace.yaml
kubectl apply -f k9s/postgresql.yaml
kubectl apply -f k9s/configmap.yaml
kubectl apply -f k9s/secret.yaml

echo "Waiting for PostgreSQL to start..."
for i in {1..30}; do
    POSTGRES_STATUS=$(kubectl get pods -n banking -l app=postgresql -o jsonpath='{.items[0].status.phase}')
    if [ "$POSTGRES_STATUS" = "Running" ]; then
        echo "PostgreSQL is running!"
        break
    fi
    echo "Waiting for PostgreSQL... ($i/30)"
    sleep 5
done

# Check PostgreSQL logs to see if it's ready
echo "Checking PostgreSQL logs..."
kubectl logs -n banking -l app=postgresql --tail=10

echo "Deploying banking API..."
kubectl apply -f k9s/deployment.yaml
kubectl apply -f k9s/service.yaml

echo "Waiting for banking API..."
for i in {1..30}; do
    BANKING_STATUS=$(kubectl get pods -n banking -l app=banking-api -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "Unknown")
    if [ "$BANKING_STATUS" = "Running" ]; then
        echo "Banking API is running!"
        break
    fi
    echo "Waiting for Banking API... ($i/30)"
    sleep 5
done

echo "Current status:"
kubectl get pods -n banking

echo "To access your application:"
kubectl port-forward -n banking service/banking-api 8080:80