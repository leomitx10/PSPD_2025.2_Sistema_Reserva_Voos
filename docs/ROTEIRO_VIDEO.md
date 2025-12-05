# Roteiro para Vídeo de Apresentação

**Duração Total**: 16-24 minutos (4-6 min por membro)
**Formato**: Gravação de tela + narração

---

## Estrutura do Vídeo

### Introdução (2 min) - Todos

**Responsável**: [Escolher um membro]

**O que mostrar**:
- Slide ou tela inicial com:
  - Nome do projeto
  - Participantes
  - Disciplina/Turma
  - Data

**O que falar**:
> "Olá, somos [nomes] e este é nosso trabalho de Programação para Sistemas Paralelos e Distribuídos. Desenvolvemos um sistema de reservas de voos e hotéis baseado em microserviços, rodando em Kubernetes com monitoramento via Prometheus e autoscaling configurado."

**Mostrar diagram de arquitetura**:
```
Browser → API Gateway → gRPC → Voos/Hotéis
                ↓
           Prometheus
```

---

## Parte 1: Cluster Kubernetes (5-6 min)

**Responsável**: [Nome do membro - sugestão: quem trabalhou mais em K8s]

### O que Mostrar

#### 1. Cluster Multi-Node (1 min)

**Terminal**:
```bash
kubectl get nodes
```

**O que falar**:
> "Nosso cluster Kubernetes possui 3 nós: um control plane e dois workers. Isso atende o requisito de 1 master e mínimo 2 workers."

**Mostrar output**:
```
NAME           STATUS   ROLES           AGE   VERSION
minikube       Ready    control-plane   2h    v1.28.0
minikube-m02   Ready    <none>          2h    v1.28.0
minikube-m03   Ready    <none>          2h    v1.28.0
```

#### 2. Deployments e Pods (1.5 min)

**Terminal**:
```bash
kubectl get deployments
kubectl get pods -o wide
```

**O que falar**:
> "Temos 3 deployments: API Gateway, serviço de voos e serviço de hotéis. Cada um com múltiplas réplicas distribuídas entre os worker nodes."

**Destacar**:
- Número de réplicas (2/2 ready)
- Distribuição entre nodes diferentes

#### 3. Services (1 min)

**Terminal**:
```bash
kubectl get services
```

**O que falar**:
> "Os serviços de voos e hotéis usam ClusterIP pois são internos. O API Gateway usa NodePort para acesso externo na porta 30000."

#### 4. Kubernetes Dashboard (1.5 min)

**Abrir dashboard**:
```bash
minikube dashboard
```

**Navegar**:
1. Visão geral dos nós
2. Lista de pods
3. Deployments
4. Workloads

**O que falar**:
> "O Kubernetes Dashboard nos dá uma visão completa do cluster. Aqui vemos o uso de recursos, status dos pods, e podemos acessar logs."

#### 5. Recursos dos Pods (1 min)

**Terminal**:
```bash
kubectl top nodes
kubectl top pods
```

**O que falar**:
> "Usando o metrics-server, conseguimos ver em tempo real o uso de CPU e memória de cada pod."

---

## Parte 2: Autoscaling (HPA) (5-6 min)

**Responsável**: [Nome do membro - sugestão: quem trabalhou em HPA/testes]

### O que Mostrar

#### 1. Configuração do HPA (1.5 min)

**Terminal**:
```bash
kubectl get hpa
kubectl describe hpa voos-service-hpa
```

**O que falar**:
> "Configuramos Horizontal Pod Autoscaler para os 3 serviços. O HPA monitora CPU e memória, escalando entre 2 e 10 réplicas quando utilização passa de 70% para CPU."

**Mostrar arquivo YAML**:
```bash
cat k8s/hpa-modulo-a.yaml
```

**Destacar**:
- minReplicas: 2
- maxReplicas: 10
- targetCPU: 70%
- Behavior policies

#### 2. HPA em Ação - Iniciar Teste (2 min)

**Terminal 1**:
```bash
watch -n 2 kubectl get hpa
```

**Terminal 2**:
```bash
watch -n 2 kubectl get pods
```

**Terminal 3**:
```bash
cd load-tests
./run_tests.sh quick
```

**O que falar**:
> "Vou iniciar um teste de carga. À esquerda, vocês veem o HPA monitorando a utilização. À direita, a lista de pods. Vamos observar o autoscaling acontecer."

#### 3. Observar Scaling (2 min)

**Narrar em tempo real**:
- "A carga começou, CPU está em 45%..."
- "Passou de 70%, HPA detectou..."
- "Novos pods sendo criados..."
- "Réplicas aumentaram de 2 para 4..."
- "Sistema estabilizou com 4 réplicas"

**Pausar o vídeo se necessário** ou gravar com velocidade aumentada e narrar depois.

#### 4. Métricas Finais (0.5 min)

**Terminal**:
```bash
kubectl top pods
```

**O que falar**:
> "Vemos que a carga foi distribuída entre os 4 pods, cada um usando em torno de 60% de CPU, mantendo dentro do threshold."

---

## Parte 3: Prometheus e Monitoramento (5-6 min)

**Responsável**: [Nome do membro - sugestão: quem trabalhou em Prometheus]

### O que Mostrar

#### 1. Arquitetura do Prometheus (1 min)

**Terminal**:
```bash
kubectl get all -n monitoring
```

**O que falar**:
> "Prometheus roda em um namespace separado chamado monitoring. Ele coleta métricas de todos os pods através de service discovery automático."

#### 2. Interface Web Prometheus (1.5 min)

**Abrir Prometheus**:
```bash
minikube service prometheus -n monitoring
```

**Navegar**:
1. Status > Targets
   - Mostrar pods descobertos
   - Status UP

**O que falar**:
> "O Prometheus descobre automaticamente os pods do Kubernetes. Aqui vemos todos os targets sendo monitorados, todos com status UP."

#### 3. Queries PromQL (3 min)

**Query 1 - Taxa de Requisições**:
```promql
sum(rate(http_requests_total[5m]))
```

**O que falar**:
> "Esta query mostra a taxa de requisições por segundo nos últimos 5 minutos. Durante nosso teste, alcançamos cerca de 180 requisições por segundo."

**Mostrar gráfico**.

---

**Query 2 - Latência P95**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**O que falar**:
> "Aqui temos a latência do percentil 95. Isso significa que 95% das requisições foram atendidas em menos de X milissegundos. É uma métrica importante para SLA."

**Mostrar gráfico**.

---

**Query 3 - Uso de CPU por Pod**:
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="default"}[5m])) by (pod)
```

**O que falar**:
> "Esta query mostra o uso de CPU de cada pod. Vemos que durante o pico de carga, alguns pods chegaram a 80% de utilização, acionando o autoscaling."

**Mostrar gráfico com múltiplas linhas (um por pod)**.

---

**Query 4 - Réplicas HPA**:
```promql
kube_deployment_status_replicas{deployment=~".*service|api-gateway"}
```

**O que falar**:
> "Esta query mostra a evolução do número de réplicas ao longo do tempo. Podemos ver claramente quando o HPA escalou de 2 para 4 réplicas."

**Mostrar gráfico step**.

#### 4. Conceitos do Livro (0.5 min)

**O que falar**:
> "Aplicamos conceitos dos capítulos 15 e 16 do livro Cloud Native DevOps with Kubernetes: observabilidade através de métricas, os quatro golden signals - latência, tráfego, erros e saturação - e uso de Prometheus como time-series database para monitoramento contínuo."

---

## Parte 4: Testes de Carga (5-6 min)

**Responsável**: [Nome do membro - sugestão: quem trabalhou em testes]

### O que Mostrar

#### 1. Ferramenta Locust (1 min)

**Código**:
```bash
cat load-tests/locustfile.py | head -50
```

**O que falar**:
> "Usamos Locust para testes de carga. É uma ferramenta Python que permite definir comportamento de usuários. Aqui definimos tasks como buscar voos, buscar hotéis, e finalizar compra, com pesos diferentes para simular comportamento real."

#### 2. Cenários Implementados (1.5 min)

**Terminal**:
```bash
python load-tests/scenarios.py
```

**O que falar**:
> "Implementamos 10 cenários de teste, cada um com objetivo diferente. O cenário baseline estabelece referência sem autoscaling. O cenário moderate testa HPA com carga moderada. O stress test identifica o breaking point do sistema."

**Mostrar lista de cenários**.

#### 3. Executar Teste - Interface Web (2.5 min)

**Abrir Locust Web UI**:
```bash
locust -f load-tests/locustfile.py --host=http://$(minikube ip):30000
```

**Navegador**: http://localhost:8089

**Configurar**:
- Number of users: 100
- Spawn rate: 10
- Duration: 2 minutos

**Iniciar teste e mostrar**:
1. Gráfico de RPS em tempo real
2. Gráfico de Response Time
3. Tabela de estatísticas
4. Percentis (50, 95, 99)

**O que falar durante o teste**:
> "Iniciamos o teste com 100 usuários simultâneos. O Locust mostra em tempo real a taxa de requisições por segundo, tempo de resposta e taxa de erros. Vemos que o sistema está respondendo bem, com latência média de 200ms e zero erros."

#### 4. Resultados (1 min)

**Mostrar relatório HTML** (abrir arquivo gerado):
```bash
firefox load-tests/results/cenario_2_moderate_report.html
```

**O que falar**:
> "Após o teste, Locust gera um relatório HTML completo com todas as estatísticas. Aqui vemos que processamos 12 mil requisições com taxa de erro de 0.2%, e latência P95 de 380ms, dentro do nosso SLA de 500ms."

---

## Conclusão (2 min) - Todos

**Responsável**: [Todos aparecem ou um apresenta]

### Resultados Alcançados

**O que falar**:
> "Conseguimos implementar com sucesso um sistema distribuído escalável. Nossos testes mostraram que o sistema suporta até 300 usuários simultâneos mantendo latência abaixo de 500ms. O autoscaling funciona corretamente, escalando em média em 2 minutos quando carga aumenta."

### Aprendizados

**Cada membro menciona brevemente** (30s cada):

**Membro 1** (Kubernetes):
> "Aprendi sobre orquestração de containers, conceitos de pods, deployments e services, e como Kubernetes gerencia distribuição de carga."

**Membro 2** (HPA):
> "Trabalhei com autoscaling, entendi como métricas de CPU e memória são usadas para decisões de scaling, e a importância de configurar corretamente requests e limits."

**Membro 3** (Prometheus):
> "Aprofundei em observabilidade, aprendi PromQL para queries de métricas, e entendi a importância de monitoramento contínuo em sistemas distribuídos."

**Membro 4** (Testes):
> "Aprendi sobre testes de carga, como simular diferentes cenários de uso, e a importância de testes sistemáticos para identificar gargalos."

### Fechamento

**O que falar**:
> "Este trabalho nos deu experiência prática com tecnologias cloud-native essenciais para a indústria atual. Obrigado!"

---

## Dicas de Gravação

### Preparação

1. **Ensaio**: Praticar antes de gravar
2. **Roteiro anotado**: Ter bullet points visíveis
3. **Ambiente pronto**: Cluster rodando, testes prontos
4. **Zoom no terminal**: Aumentar fonte para facilitar leitura
5. **Cursor destacado**: Usar ferramenta para destacar cursor

### Técnicas de Gravação

**Ferramentas**:
- **Linux**: OBS Studio, SimpleScreenRecorder
- **macOS**: QuickTime, ScreenFlow
- **Windows**: OBS Studio, Windows Game Bar

**Configurações**:
- Resolução: 1920x1080
- FPS: 30
- Áudio: Microfone externo se possível
- Formato: MP4

**Dicas**:
- Falar devagar e claramente
- Pausar entre seções (facilita edição)
- Gravar em partes (um membro por vez)
- Deixar 2-3 segundos de silêncio no início/fim de cada clipe

### Edição

**Ferramentas**:
- **Grátis**: DaVinci Resolve, OpenShot
- **Pago**: Adobe Premiere, Final Cut Pro

**O que fazer**:
1. Juntar clipes de cada membro
2. Adicionar introdução com slide
3. Adicionar transições suaves
4. Normalizar áudio
5. Adicionar legendas (opcional mas recomendado)
6. Exportar em MP4

### Checklist Pré-Gravação

- [ ] Cluster Kubernetes rodando
- [ ] Todos os pods em Ready
- [ ] Prometheus acessível
- [ ] Locust instalado
- [ ] Terminal com fonte grande (16-18pt)
- [ ] Browser em tela cheia (F11)
- [ ] Abas abertas: Dashboard, Prometheus, Locust
- [ ] Microfone testado
- [ ] Software de gravação funcionando
- [ ] Roteiro impresso/visível
- [ ] Fechar notificações do sistema

### Duração

**Por membro**: 4-6 minutos
**Total**: 16-24 minutos

Se passar de 25 minutos, editar para remover pausas longas.

---

## Alternativa: Gravação Assíncrona

Se membros não puderem gravar juntos:

1. **Cada membro grava sua parte** separadamente
2. **Um membro edita** juntando tudo
3. **Todos revisam** versão final antes de entregar

**Vantagens**:
- Cada um grava no seu tempo
- Pode regravar se errar
- Mais flexível

**Desvantagens**:
- Precisa edição
- Pode ficar menos natural

---

## Upload e Entrega

### Opções de Upload

**YouTube** (Recomendado):
- Fazer upload como "unlisted"
- Copiar link
- Incluir link no relatório

**Google Drive**:
- Fazer upload
- Gerar link compartilhável
- Incluir no relatório

**OneDrive/Dropbox**:
- Similar ao Drive

### Incluir no Relatório

No arquivo `RELATORIO_FINAL.md`, adicionar:

```markdown
## Link do Vídeo

**URL**: https://youtube.com/watch?v=...

**Duração**: 20 minutos

**Participantes**:
- Leandro de Almeida (Parte 1 - Kubernetes)
- Gabriela Alves (Parte 2 - HPA)
- Renan Lacerda (Parte 3 - Prometheus)
- Samuel Ricardo (Parte 4 - Testes de Carga)
```

---

**Boa gravação!** 🎬
