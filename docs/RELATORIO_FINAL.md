# Relatório Final - Sistema de Reserva de Voos

**Disciplina**: Programação para Sistemas Paralelos e Distribuídos
**Curso**: [Seu Curso]
**Turma**: [Sua Turma]
**Semestre**: 2025.2
**Data**: [Data de Entrega]

---

## Identificação dos Participantes

| Nome Completo | Matrícula | GitHub | Email |
|---------------|-----------|--------|-------|
| Leandro de Almeida | XXXXXX | [@leomitx10](https://github.com/leomitx10) | leandro@email.com |
| Gabriela Alves | XXXXXX | [@gaubiela](https://github.com/gaubiela) | gabriela@email.com |
| Renan Lacerda | XXXXXX | [@LacerdaRenan](https://github.com/LacerdaRenan) | renan@email.com |
| Samuel Ricardo | XXXXXX | [@SamuelRicardoDS](https://github.com/SamuelRicardoDS) | samuel@email.com |

---

## Sumário

1. [Introdução](#1-introdução)
2. [Metodologia](#2-metodologia)
3. [Experiência de Montagem do Kubernetes](#3-experiência-de-montagem-do-kubernetes)
4. [Monitoramento e Observabilidade](#4-monitoramento-e-observabilidade)
5. [Aplicação](#5-aplicação)
6. [Cenários de Teste](#6-cenários-de-teste)
7. [Análise Comparativa](#7-análise-comparativa)
8. [Conclusão](#8-conclusão)
9. [Referências](#9-referências)
10. [Anexos](#10-anexos)

---

## 1. Introdução

### 1.1 Contexto

Este trabalho consiste na implementação e avaliação de um sistema distribuído baseado em microserviços utilizando Kubernetes, com foco em monitoramento, observabilidade e autoscaling. O objetivo é aplicar os conceitos de cloud native computing, containerização e orquestração estudados na disciplina.

### 1.2 Objetivos

**Objetivos Principais**:
1. Implementar aplicação baseada em microserviços com comunicação gRPC
2. Criar cluster Kubernetes com mínimo de 1 master e 2 workers
3. Configurar autoscaling (HPA) para escalabilidade horizontal
4. Implementar monitoramento com Prometheus
5. Realizar testes de carga para avaliar performance e escalabilidade

**Objetivos Secundários**:
- Compreender mecanismos de observabilidade em sistemas distribuídos
- Identificar gargalos e limites da aplicação
- Otimizar configurações para melhor relação performance/custo
- Aplicar conceitos do livro "Cloud Native DevOps with Kubernetes" (Capítulos 15 e 16)

### 1.3 Escopo

O trabalho abrange:
- Sistema de Reservas de Voos e Hotéis
- 3 microserviços (API Gateway, Voos, Hotéis)
- Cluster Kubernetes multi-node
- Prometheus para métricas
- Horizontal Pod Autoscaler (HPA)
- Testes de carga com Locust
- Mínimo 5 cenários de teste diferentes

### 1.4 Visão Geral do Relatório

Este relatório está estruturado da seguinte forma:
- **Seção 2**: Descreve como o grupo se organizou e a metodologia adotada
- **Seção 3**: Experiência de montagem do cluster Kubernetes
- **Seção 4**: Configuração e uso do Prometheus
- **Seção 5**: Detalhes da aplicação desenvolvida
- **Seções 6-7**: Resultados dos testes e análises
- **Seção 8**: Conclusões e aprendizados
- **Seções 9-10**: Referências e anexos

---

## 2. Metodologia

### 2.1 Organização do Grupo

**Divisão de Responsabilidades**:

| Membro | Responsabilidades Principais |
|--------|------------------------------|
| Leandro de Almeida | Desenvolvimento do Módulo A (Voos - Python), Testes de Carga |
| Gabriela Alves | Desenvolvimento do Módulo B (Hotéis - Go), Documentação |
| Renan Lacerda | Desenvolvimento do Módulo P (API Gateway - Node.js), Kubernetes |
| Samuel Ricardo | Configuração Prometheus, Análise de Resultados |

**Observação**: Todos os membros participaram de todas as etapas em diferentes níveis, com rotação de tarefas para garantir aprendizado completo.

### 2.2 Cronograma de Reuniões

#### Reunião 1 - [Data] - Planejamento Inicial
**Duração**: 2 horas
**Local**: [Presencial/Online]

**Pautas**:
- Discussão dos requisitos do trabalho
- Escolha da aplicação (Sistema de Reservas)
- Definição de tecnologias (Python, Go, Node.js)
- Divisão inicial de tarefas

**Decisões Tomadas**:
- Usar Minikube para cluster Kubernetes
- Prometheus para monitoramento
- Locust para testes de carga
- Repositório GitHub para versionamento

**Tarefas Atribuídas**:
- [Nome]: Configurar repositório Git
- [Nome]: Estudar Prometheus (Cap 15-16 do livro)
- [Nome]: Implementar Módulo A
- [Nome]: Implementar Módulo B

---

#### Reunião 2 - [Data] - Revisão de Progresso
**Duração**: 1.5 horas
**Local**: [Presencial/Online]

**Pautas**:
- Review dos módulos desenvolvidos
- Discussão sobre integração gRPC
- Primeiros testes de containerização

**Problemas Encontrados**:
- Dificuldade com serialização de dados no gRPC (Go ↔ Python)
- Conflito de portas nos containers

**Soluções Implementadas**:
- Revisar definições .proto para compatibilidade
- Usar network mode bridge no Docker Compose

**Próximos Passos**:
- Iniciar configuração do Kubernetes
- Testar comunicação entre microserviços

---

#### Reunião 3 - [Data] - Kubernetes e Prometheus
**Duração**: 3 horas
**Local**: [Presencial/Online]

**Pautas**:
- Demonstração do cluster Kubernetes funcionando
- Configuração do Prometheus
- Planejamento dos cenários de teste

**Realizações**:
- Cluster multi-node configurado
- Todos os serviços deployados
- HPA configurado
- Prometheus coletando métricas

**Desafios**:
- HPA inicialmente não escalava (metrics-server não instalado)
- Prometheus não descobria pods (RBAC incorreto)

**Soluções**:
- Habilitar addon metrics-server no Minikube
- Corrigir ServiceAccount e ClusterRole do Prometheus

---

#### Reunião 4 - [Data] - Testes de Carga
**Duração**: 4 horas
**Local**: [Presencial/Online]

**Pautas**:
- Execução dos cenários de teste
- Coleta de métricas
- Análise preliminar de resultados

**Atividades Realizadas**:
- Executados 7 cenários de teste
- Coletadas métricas de CPU, memória, latência, RPS
- Identificados gargalos
- Capturados screenshots do Prometheus e Locust

**Descobertas**:
- Sistema satura com ~300 usuários simultâneos
- HPA funciona bem mas demora ~2min para scale-up completo
- Módulo P (Gateway) é o gargalo principal

---

#### Reunião 5 - [Data] - Finalização e Documentação
**Duração**: 2 horas
**Local**: [Presencial/Online]

**Pautas**:
- Revisão dos resultados
- Escrita do relatório
- Gravação do vídeo de apresentação

**Realizações**:
- Relatório completo
- Vídeo gravado e editado
- Arquivos organizados para entrega

---

### 2.3 Ferramentas Utilizadas

| Ferramenta | Versão | Uso |
|------------|--------|-----|
| Kubernetes | 1.28.0 | Orquestração de containers |
| Minikube | v1.32.0 | Cluster local Kubernetes |
| Docker | 24.0.7 | Containerização |
| Python | 3.11 | Módulo A (Voos) |
| Go | 1.21 | Módulo B (Hotéis) |
| Node.js | 20.x | Módulo P (API Gateway) |
| gRPC | - | Comunicação inter-serviços |
| Prometheus | 2.48.0 | Monitoramento |
| Locust | 2.20.0 | Testes de carga |
| kubectl | 1.28.0 | CLI Kubernetes |
| Git/GitHub | - | Versionamento |

### 2.4 Metodologia de Desenvolvimento

**Abordagem**: Desenvolvimento iterativo e incremental

**Fases**:
1. **Fase 1 - Desenvolvimento dos Microserviços** (Semana 1-2)
   - Implementação individual de cada módulo
   - Testes unitários
   - Containerização com Docker

2. **Fase 2 - Integração gRPC** (Semana 2-3)
   - Definição de .proto files
   - Implementação de clients e servers
   - Testes de integração

3. **Fase 3 - Kubernetes Setup** (Semana 3-4)
   - Criação do cluster
   - Deployments e Services
   - Configuração de HPA

4. **Fase 4 - Monitoramento** (Semana 4)
   - Instalação do Prometheus
   - Configuração de scraping
   - Criação de queries

5. **Fase 5 - Testes e Otimização** (Semana 5-6)
   - Execução de cenários
   - Coleta de métricas
   - Análise e ajustes

6. **Fase 6 - Documentação** (Semana 6-7)
   - Escrita do relatório
   - Gravação do vídeo
   - Preparação para entrega

---

## 3. Experiência de Montagem do Kubernetes

### 3.1 Escolha da Ferramenta

**Opções Avaliadas**:
1. **Minikube** ✅ Escolhido
2. **Kind** (Kubernetes in Docker)
3. **K3s** (Lightweight Kubernetes)
4. **MicroK8s** (Canonical)
5. **Cloud Providers** (GKE, EKS, AKS) - descartado por custo

**Critérios de Decisão**:
- Suporte multi-node (requisito do trabalho)
- Facilidade de instalação
- Documentação disponível
- Experiência prévia do grupo

**Justificativa**: Minikube foi escolhido por oferecer suporte multi-node, ter boa documentação e ser amplamente usado em ambientes de desenvolvimento.

### 3.2 Processo de Instalação

#### 3.2.1 Instalação do Minikube

**Ambiente**: Ubuntu 22.04 LTS (WSL2 no Windows)

```bash
# Download
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Instalação
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verificação
minikube version
# Output: minikube version: v1.32.0
```

**Dificuldades**: Nenhuma nesta etapa.

#### 3.2.2 Instalação do kubectl

```bash
# Download
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Permissão de execução
chmod +x kubectl

# Mover para PATH
sudo mv kubectl /usr/local/bin/

# Verificação
kubectl version --client
# Output: Client Version: v1.28.0
```

**Dificuldades**: Nenhuma.

#### 3.2.3 Criação do Cluster Multi-Node

```bash
# Iniciar cluster com 3 nós
minikube start \
  --nodes=3 \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker

# Verificar nós
kubectl get nodes
```

**Output Esperado**:
```
NAME           STATUS   ROLES           AGE   VERSION
minikube       Ready    control-plane   2m    v1.28.0
minikube-m02   Ready    <none>          1m    v1.28.0
minikube-m03   Ready    <none>          1m    v1.28.0
```

**Dificuldades Encontradas**:
1. **Problema**: Minikube não iniciava com driver Docker no Windows
   - **Causa**: Docker Desktop não estava rodando
   - **Solução**: Iniciar Docker Desktop antes do Minikube

2. **Problema**: Nós adicionais ficavam em estado NotReady
   - **Causa**: Recursos insuficientes (RAM)
   - **Solução**: Aumentar memória alocada de 4GB para 8GB

#### 3.2.4 Habilitação de Addons

```bash
# Metrics Server (necessário para HPA)
minikube addons enable metrics-server

# Dashboard
minikube addons enable dashboard

# Verificar
minikube addons list | grep enabled
```

**Dificuldades**:
- Metrics-server demorou ~2 minutos para ficar pronto
- Solução: Aguardar com `kubectl wait`

### 3.3 Configuração do Cluster

#### 3.3.1 Arquitetura Implementada

```
┌─────────────────────────────────────────────────┐
│           KUBERNETES CLUSTER                     │
│                                                   │
│  ┌─────────────────────────────────────────┐    │
│  │       Control Plane (minikube)          │    │
│  │  - API Server                            │    │
│  │  - Scheduler                             │    │
│  │  - Controller Manager                    │    │
│  │  - etcd                                  │    │
│  └─────────────────────────────────────────┘    │
│              │                                    │
│      ┌───────┴────────┐                         │
│      ▼                ▼                         │
│  ┌─────────┐    ┌─────────┐                    │
│  │ Worker1 │    │ Worker2 │                    │
│  │ (m02)   │    │ (m03)   │                    │
│  └─────────┘    └─────────┘                    │
│                                                   │
│  Namespaces:                                     │
│  - default (aplicação)                           │
│  - monitoring (Prometheus)                       │
│  - kube-system (componentes core)                │
└─────────────────────────────────────────────────┘
```

#### 3.3.2 Deployments Criados

**Arquivo**: `k8s/deployment-modulo-a.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voos-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: voos-service
  template:
    metadata:
      labels:
        app: voos-service
    spec:
      containers:
      - name: voos-service
        image: modulo-a:v1
        imagePullPolicy: Never
        ports:
        - containerPort: 50051
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          tcpSocket:
            port: 50051
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          tcpSocket:
            port: 50051
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Conceitos Aplicados**:
- **Resources requests/limits**: Garantir alocação de recursos
- **Liveness/Readiness probes**: Auto-recuperação e health checks
- **imagePullPolicy: Never**: Usar imagens locais do Minikube

**Deployments Similares**:
- `deployment-modulo-b.yaml` (Hotéis Service)
- `deployment-modulo-p.yaml` (API Gateway)

#### 3.3.3 Services

**ClusterIP** (interno):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: voos-service
spec:
  type: ClusterIP
  selector:
    app: voos-service
  ports:
  - port: 50051
    targetPort: 50051
    protocol: TCP
```

**NodePort** (externo):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
spec:
  type: NodePort
  selector:
    app: api-gateway
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30000
    protocol: TCP
```

**Justificativa**:
- Voos e Hotéis são internos (ClusterIP) - só precisam comunicar com Gateway
- Gateway é externo (NodePort) - precisa receber tráfego dos usuários/testes

#### 3.3.4 Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: voos-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: voos-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 15
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
```

**Conceitos Aplicados** (Relacionados ao Livro - Cap 15):
- **Métricas múltiplas**: CPU e memória
- **Behavior policies**: Controlar velocidade de scaling
- **Stabilization window**: Evitar flapping (scale up/down rápido)

**Parâmetros Escolhidos**:
- `minReplicas: 2` - Mínimo para alta disponibilidade
- `maxReplicas: 10` - Baseado em recursos disponíveis do cluster
- `targetCPU: 70%` - Balanceamento entre utilização e margem
- `scaleDown: 300s` - Aguardar 5min antes de remover pods (evitar oscilação)

### 3.4 Desafios e Soluções

#### Desafio 1: HPA não escalava

**Sintomas**:
```bash
kubectl get hpa
# TARGETS: <unknown>/70%
```

**Diagnóstico**:
```bash
kubectl describe hpa voos-service-hpa
# Events: unable to get metrics for resource cpu
```

**Causa Raiz**: Metrics Server não estava instalado

**Solução**:
```bash
minikube addons enable metrics-server
kubectl wait --for=condition=ready pod -n kube-system -l k8s-app=metrics-server
```

**Aprendizado**: HPA depende do Metrics Server para coletar métricas de CPU/memória.

---

#### Desafio 2: Imagens Docker não encontradas

**Sintomas**:
```bash
kubectl get pods
# voos-service-xxx   0/1   ImagePullBackOff
```

**Causa Raiz**: Imagens construídas no Docker local, mas Kubernetes procurava em registry

**Solução**:
```bash
# Configurar Docker para usar daemon do Minikube
eval $(minikube docker-env)

# Rebuild imagens
docker build -t modulo-a:v1 ./module-a

# Usar imagePullPolicy: Never nos deployments
```

**Aprendizado**: Em ambientes locais, usar `imagePullPolicy: Never` e buildar imagens dentro do Minikube.

---

#### Desafio 3: Pods distribuídos desigualmente

**Sintomas**: Todos os pods em um único worker node

**Diagnóstico**:
```bash
kubectl get pods -o wide
# Todos em minikube-m02
```

**Causa**: Scheduler padrão usa "least allocated"

**Solução** (opcional): Adicionar `podAntiAffinity` para forçar distribuição

**Aprendizado**: Kubernetes scheduler funciona bem, mas pode-se ajustar com affinity/anti-affinity se necessário.

### 3.5 Comandos Úteis Utilizados

```bash
# Ver estado do cluster
kubectl cluster-info
kubectl get nodes
kubectl get all -n default

# Aplicar configurações
kubectl apply -f k8s/
kubectl rollout status deployment voos-service

# Debugging
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl exec -it <pod-name> -- /bin/sh

# Escalar manualmente
kubectl scale deployment voos-service --replicas=5

# Ver métricas
kubectl top nodes
kubectl top pods

# Ver HPA
kubectl get hpa
kubectl describe hpa voos-service-hpa

# Acessar serviços
minikube service api-gateway
kubectl port-forward service/api-gateway 3000:3000
```

### 3.6 Arquivos de Configuração

Todos os arquivos estão em `k8s/`:
- `deployment-modulo-a.yaml` - Deployment do serviço de voos
- `deployment-modulo-b.yaml` - Deployment do serviço de hotéis
- `deployment-modulo-p.yaml` - Deployment do API Gateway
- `service-modulo-a.yaml` - Service ClusterIP para voos
- `service-modulo-b.yaml` - Service ClusterIP para hotéis
- `service-modulo-p.yaml` - Service NodePort para gateway
- `hpa-modulo-a.yaml` - HPA para voos
- `hpa-modulo-b.yaml` - HPA para hotéis
- `hpa-modulo-p.yaml` - HPA para gateway

Ver seção Anexos para conteúdo completo.

### 3.7 Lições Aprendidas

1. **Planejamento de Recursos**: Definir resources requests/limits desde o início é crucial para HPA funcionar
2. **Probes são importantes**: Liveness e readiness probes evitam pods não-funcionais receberem tráfego
3. **Metrics Server é essencial**: Sem ele, HPA não funciona
4. **imagePullPolicy**: Em dev local, usar `Never`; em produção, usar `Always` ou `IfNotPresent`
5. **Stabilization Window**: Evita oscilações desnecessárias de scaling
6. **Documentação**: Manter documentação atualizada facilita debugging

---

## 4. Monitoramento e Observabilidade

[CONTINUA NA PRÓXIMA SEÇÃO - Descrever instalação e uso do Prometheus conforme Cap 15-16 do livro]

### 4.1 Escolha do Prometheus

[Justificar escolha, alternativas consideradas]

### 4.2 Instalação do Prometheus

[Passos detalhados]

### 4.3 Configuração

[prometheus.yml, RBAC, etc.]

### 4.4 Queries Utilizadas

[PromQL queries principais]

### 4.5 Conceitos Aplicados do Livro

[Relacionar com Cap 15-16]

---

## 5. Aplicação

[Descrever sistema de reservas, arquitetura, gRPC, etc.]

---

## 6. Cenários de Teste

[Documentar cada cenário executado conforme metodologia]

---

## 7. Análise Comparativa

[Tabelas e gráficos comparando cenários]

---

## 8. Conclusão

### 8.1 Conclusão Geral

[Texto conclusivo sobre experiência, aprendizados, desafios]

### 8.2 Autoavaliação Individual

#### [Nome do Membro 1]

**Partes em que mais trabalhei**:
- [Listar contribuições]

**Principais Aprendizados**:
- [Descrever o que aprendeu]

**Dificuldades Encontradas**:
- [Descrever desafios]

**Nota de Autoavaliação**: [0-10]

---

[Repetir para cada membro]

---

## 9. Referências

1. Arundel, J. and Domingus, J. "Cloud Native DevOps with Kubernetes – Building, Deploying and Scaling Modern Applications in the Cloud", O´Reilly, 2019

2. Kubernetes Documentation. Disponível em: https://kubernetes.io/docs/

3. Prometheus Documentation. Disponível em: https://prometheus.io/docs/

4. Locust Documentation. Disponível em: https://docs.locust.io/

5. [Outras referências utilizadas]

---

## 10. Anexos

### Anexo A: Arquivos de Configuração Kubernetes

[Conteúdo dos YAMLs]

### Anexo B: Código-Fonte dos Microserviços

[Trechos relevantes ou link GitHub]

### Anexo C: Resultados Completos dos Testes

[Tabelas detalhadas, gráficos]

### Anexo D: Screenshots

[Prometheus queries, Kubernetes Dashboard, Locust, etc.]

### Anexo E: Instruções de Execução

[Como replicar o projeto passo a passo]

---

**Fim do Relatório**
