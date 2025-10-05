# Sistema de Reserva de Voos - PSPD 2025.2

Sistema distribuído de reservas de voos e hotéis usando gRPC, WebSocket e Kubernetes.

## Participantes

<table>
  <tr>
    <td align="center"><a href="https://github.com/leomitx10"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/90487905?v=4" width="100px;" alt=""/><br /><sub><b>Leandro de Almeida</b></sub></a><br />
    <td align="center"><a href="https://github.com/gaubiela"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/92053289?v=4" width="100px;" alt=""/><br /><sub><b>Gabriela Alves</b></sub></a><br /><a href="Link git" title="Rocketseat"></a></td>
    <td align="center">
  </tr>
</table>


## Arquitetura

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────────┐
│  API Gateway    │
│   (Node.js)     │
│   Porta 3000    │
└────────┬────────┘
         │ gRPC
    ┌────┴────┐
    ▼         ▼
┌─────────┐  ┌──────────┐
│  Voos   │  │  Hotéis  │
│ (Python)│  │   (Go)   │
│ :50051  │  │  :50052  │
└─────────┘  └──────────┘
```

## Funcionalidades gRPC

- **Unary RPC**: Busca de voos e hotéis
- **Server Streaming**: Monitoramento de voo em tempo real
- **Client Streaming**: Finalização de compra
- **Bidirectional Streaming**: Chat de suporte via WebSocket

## Como Executar

### Docker Compose (Recomendado)

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

**Acesse**: http://localhost:3000

### Kubernetes/Minikube

```bash
# Iniciar Minikube
minikube start

# Instalar kubectl (se necessário)
sudo snap install kubectl --classic

# Aplicar manifestos
kubectl apply -f k8s/

# Verificar status
kubectl get pods
kubectl get services

# Acessar aplicação
minikube service api-gateway --url
```

**Acesse**: URL retornada pelo comando acima (ex: http://192.168.49.2:30000)

## Teste de Performance

```bash
cd performance-test
pip install -r requirements.txt
python test_grpc_vs_rest.py
```

## Tecnologias

- **Python 3.9** + gRPC - Serviço de Voos
- **Go 1.21** + gRPC - Serviço de Hotéis  
- **Node.js** + Express - API Gateway
- **WebSocket** - Chat em tempo real
- **Docker** + **Kubernetes** - Deployment

## Funcionalidades

- Busca de voos e hotéis
- Pacotes combinados
- Carrinho de compras
- Monitoramento em tempo real
- Chat de suporte

---

**Projeto PSPD 2025.2 - UnB**
