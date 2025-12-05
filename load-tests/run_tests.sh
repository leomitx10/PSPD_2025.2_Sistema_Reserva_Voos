#!/bin/bash

###############################################################################
# Script de Execução de Testes de Carga
# Sistema de Reserva de Voos - PSPD 2025.2
###############################################################################

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
RESULTS_DIR="results"
MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "localhost")
API_PORT="30000"
HOST="http://${MINIKUBE_IP}:${API_PORT}"

# Criar diretório de resultados
mkdir -p ${RESULTS_DIR}

print_header() {
    echo -e "${BLUE}"
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_dependencies() {
    print_header "Verificando Dependências"

    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 não encontrado!"
        exit 1
    fi
    print_success "Python3 encontrado"

    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 não encontrado!"
        exit 1
    fi
    print_success "pip3 encontrado"

    # Verificar kubectl
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl não encontrado - alguns comandos podem falhar"
    else
        print_success "kubectl encontrado"
    fi

    # Verificar Minikube
    if ! command -v minikube &> /dev/null; then
        print_warning "minikube não encontrado - usando localhost"
    else
        print_success "minikube encontrado"
    fi
}

setup_environment() {
    print_header "Configurando Ambiente de Testes"

    # Criar virtual environment se não existir
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment não encontrado. Criando..."
        python3 -m venv venv
        print_success "Virtual environment criado"
    fi

    # Ativar virtual environment
    source venv/bin/activate

    # Instalar dependências
    print_warning "Instalando dependências..."
    pip install -q -r requirements.txt
    print_success "Dependências instaladas"
}

configure_k8s() {
    local scenario=$1
    print_header "Configurando Kubernetes para: $scenario"

    # Aqui você aplicaria as configurações específicas do cenário
    # Exemplo: ajustar replicas, aplicar HPA, etc.

    case $scenario in
        "cenario_1_baseline")
            kubectl scale deployment voos-service --replicas=2
            kubectl scale deployment hoteis-service --replicas=2
            kubectl scale deployment api-gateway --replicas=2
            # Desabilitar HPA
            kubectl delete hpa --all 2>/dev/null
            ;;
        "cenario_2_moderate")
            kubectl scale deployment voos-service --replicas=2
            kubectl scale deployment hoteis-service --replicas=2
            kubectl scale deployment api-gateway --replicas=2
            # Habilitar HPA
            kubectl apply -f ../k8s/hpa-modulo-a.yaml
            kubectl apply -f ../k8s/hpa-modulo-b.yaml
            kubectl apply -f ../k8s/hpa-modulo-p.yaml
            ;;
        "cenario_3_high_load")
            kubectl scale deployment voos-service --replicas=3
            kubectl scale deployment hoteis-service --replicas=3
            kubectl scale deployment api-gateway --replicas=3
            kubectl apply -f ../k8s/hpa-modulo-a.yaml
            kubectl apply -f ../k8s/hpa-modulo-b.yaml
            kubectl apply -f ../k8s/hpa-modulo-p.yaml
            ;;
        *)
            print_warning "Cenário $scenario - configuração manual necessária"
            ;;
    esac

    # Aguardar pods estarem prontos
    print_warning "Aguardando pods estarem prontos..."
    kubectl wait --for=condition=ready pod -l app=voos-service --timeout=60s
    kubectl wait --for=condition=ready pod -l app=hoteis-service --timeout=60s
    kubectl wait --for=condition=ready pod -l app=api-gateway --timeout=60s

    print_success "Kubernetes configurado"

    # Exibir status
    echo ""
    echo "Status dos deployments:"
    kubectl get deployments
    echo ""
    echo "Status dos pods:"
    kubectl get pods
    echo ""
}

run_scenario() {
    local scenario=$1

    print_header "Executando: $scenario"

    # Configurar Kubernetes
    configure_k8s $scenario

    # Aguardar estabilização
    print_warning "Aguardando 30 segundos para estabilização..."
    sleep 30

    # Executar teste
    print_warning "Iniciando teste de carga..."

    # Comando Locust baseado no cenário
    locust -f locustfile.py \
        --host=${HOST} \
        --headless \
        --users=100 \
        --spawn-rate=10 \
        --run-time=5m \
        --html=${RESULTS_DIR}/${scenario}_report.html \
        --csv=${RESULTS_DIR}/${scenario} \
        --only-summary

    if [ $? -eq 0 ]; then
        print_success "Teste concluído com sucesso"
    else
        print_error "Teste falhou"
        return 1
    fi

    # Coletar métricas do Kubernetes
    print_warning "Coletando métricas do Kubernetes..."
    kubectl top pods > ${RESULTS_DIR}/${scenario}_k8s_metrics.txt 2>&1
    kubectl get hpa > ${RESULTS_DIR}/${scenario}_hpa_status.txt 2>&1

    # Aguardar antes do próximo teste
    print_warning "Aguardando 60 segundos antes do próximo teste..."
    sleep 60

    echo ""
}

run_all_scenarios() {
    print_header "Executando Todos os Cenários de Teste"

    scenarios=(
        "cenario_1_baseline"
        "cenario_2_moderate"
        "cenario_3_high_load"
    )

    for scenario in "${scenarios[@]}"; do
        run_scenario $scenario
    done

    print_header "Todos os Testes Concluídos"
    print_success "Resultados salvos em: ${RESULTS_DIR}/"
}

show_results() {
    print_header "Resumo dos Resultados"

    if [ -d "${RESULTS_DIR}" ]; then
        echo "Arquivos gerados:"
        ls -lh ${RESULTS_DIR}/
        echo ""

        # Mostrar resumo de cada teste
        for report in ${RESULTS_DIR}/*_stats.csv; do
            if [ -f "$report" ]; then
                echo "----------------------------------------"
                echo "Relatório: $(basename $report)"
                echo "----------------------------------------"
                head -n 5 "$report"
                echo ""
            fi
        done
    else
        print_warning "Nenhum resultado encontrado"
    fi
}

run_single_test() {
    print_header "Teste Rápido - Configuração Básica"

    print_warning "Host: ${HOST}"
    print_warning "Executando teste com 50 usuários por 2 minutos..."

    locust -f locustfile.py \
        --host=${HOST} \
        --headless \
        --users=50 \
        --spawn-rate=5 \
        --run-time=2m \
        --html=${RESULTS_DIR}/quick_test_report.html \
        --csv=${RESULTS_DIR}/quick_test \
        --only-summary

    if [ $? -eq 0 ]; then
        print_success "Teste concluído!"
        echo ""
        echo "Relatório HTML: ${RESULTS_DIR}/quick_test_report.html"
    fi
}

show_help() {
    cat << EOF
Sistema de Testes de Carga - Sistema de Reservas

Uso: $0 [OPÇÃO]

Opções:
    setup           Configura ambiente de testes
    quick           Executa teste rápido (2 min, 50 usuários)
    scenario <nome> Executa cenário específico
    all             Executa todos os cenários
    results         Mostra resumo dos resultados
    help            Mostra esta mensagem

Exemplos:
    $0 setup
    $0 quick
    $0 scenario cenario_1_baseline
    $0 all

Cenários disponíveis:
    cenario_1_baseline    - Baseline sem autoscaling
    cenario_2_moderate    - Carga moderada com HPA
    cenario_3_high_load   - Alta carga
    cenario_4_stress      - Teste de estresse
    cenario_5_spike       - Pico súbito

EOF
}

# Main
main() {
    case "${1:-help}" in
        setup)
            check_dependencies
            setup_environment
            ;;
        quick)
            check_dependencies
            setup_environment
            run_single_test
            ;;
        scenario)
            if [ -z "$2" ]; then
                print_error "Especifique o nome do cenário"
                exit 1
            fi
            check_dependencies
            setup_environment
            run_scenario $2
            ;;
        all)
            check_dependencies
            setup_environment
            run_all_scenarios
            ;;
        results)
            show_results
            ;;
        help|*)
            show_help
            ;;
    esac
}

main "$@"
