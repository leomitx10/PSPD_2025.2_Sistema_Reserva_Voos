# Script PowerShell para Windows

Write-Host "🚀 Iniciando serviços..." -ForegroundColor Green

# Aplicar configurações do Kubernetes
kubectl apply -f k8s/

Write-Host "⏳ Aguardando pods ficarem prontos..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=api-gateway --timeout=60s
kubectl wait --for=condition=ready pod -l app=voos-service --timeout=60s
kubectl wait --for=condition=ready pod -l app=hoteis-service --timeout=60s

Write-Host "🪟 Windows detectado - usando port-forward" -ForegroundColor Cyan
Write-Host "🌐 Acesse a API em: http://localhost:3000" -ForegroundColor Green
Write-Host "📝 Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

kubectl port-forward service/api-gateway 3000:3000
