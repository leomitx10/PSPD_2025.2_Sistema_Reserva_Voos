# Sistema de Reserva de Voos - PSPD 2025.2

Sistema distribuído para reserva de voos, hotéis e pacotes, desenvolvido para fins acadêmicos na disciplina de PSPD 2025.2. O projeto utiliza microserviços em diferentes linguagens, integra APIs REST e gRPC, e inclui testes de carga e monitoramento com Prometheus.

## Como rodar o projeto

### Usando Docker Compose
1. Na raiz do projeto, execute:
	```bash
	docker-compose up
	```
	Isso irá subir os principais serviços definidos em `docker-compose.yml`.

### Usando Kubernetes
1. Certifique-se que o cluster está ativo (ex: Minikube).
2. Aplique os arquivos de deployment e serviços:
	```bash
	kubectl apply -f k8s/
	```
	Isso irá subir todos os módulos e dependências no cluster.

---

## Como rodar o Prometheus Dashboard

1. Certifique-se que o cluster Kubernetes está ativo e o Prometheus está implantado:
	```bash
	kubectl get pods -n monitoring
	```
	O pod `prometheus` deve estar com status `Running`.

2. Faça o port-forward para acessar o dashboard:
	```bash
	kubectl port-forward -n monitoring svc/prometheus 9090:9090
	```

3. Acesse o dashboard em:
	[http://localhost:9090](http://localhost:9090)

---

## Como rodar os testes de carga/performance

1. Ative o ambiente virtual Python:
	```bash
	source venv/bin/activate
	```

2. Execute um dos cenários de teste:
	```bash
	cd load-tests
	python run_cenario_1_baseline.py
	# ou
	python run_cenario_2_moderate.py
	# ...
	```
	Os resultados estarão na pasta `load-tests/results/`.

3. Para rodar todos os cenários:
	```bash
	bash run_tests.sh
	```

---

## Estrutura
- `k8s/`: Arquivos de configuração do Kubernetes
- `load-tests/`: Scripts de teste de carga
- `module-a/`, `module-b/`, `module-p/`: Serviços do sistema

---

## Requisitos
- Python 3.8+
- Kubernetes (Minikube ou similar)
- Docker
- Locust

---

## Observações
- Para visualizar métricas e relatórios, acesse o Prometheus e os arquivos HTML gerados em `load-tests/results/`.
