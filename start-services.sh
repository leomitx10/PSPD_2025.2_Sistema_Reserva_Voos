#!/bin/bash

# Script para iniciar os serviços e configurar acesso multiplataforma

echo "🚀 Iniciando serviços..."

# Aplicar configurações do Kubernetes
kubectl apply -f k8s/

echo "⏳ Aguardando pods ficarem prontos..."
kubectl wait --for=condition=ready pod -l app=api-gateway --timeout=60s
kubectl wait --for=condition=ready pod -l app=voos-service --timeout=60s
kubectl wait --for=condition=ready pod -l app=hoteis-service --timeout=60s

# Detectar sistema operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    MINGW*|MSYS*|CYGWIN*)    MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "📍 Sistema detectado: ${MACHINE}"

if [ "$MACHINE" = "Windows" ]; then
    echo "🪟 Windows detectado - usando port-forward"
    echo "🌐 Acesse a API em: http://localhost:3000"
    echo "📝 Pressione Ctrl+C para parar"
    kubectl port-forward service/api-gateway 3000:3000
else
    echo "🐧 Linux/Mac detectado - usando NodePort"
    MINIKUBE_IP=$(minikube ip)
    echo "🌐 Acesse a API em: http://${MINIKUBE_IP}:30000"
    echo "📊 Para monitorar os logs, use: kubectl logs -f -l app=api-gateway"
fi
