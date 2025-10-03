# Sistema de Reserva de Voos - Módulo A (Voos)

> **Resumo:**  
> Este módulo serve para gerenciar e consultar informações de voos de forma automatizada, usando Python e gRPC. Ele permite buscar voos disponíveis, aplicar filtros (preço, companhia, horários), simular variações de preço e atrasos, e realizar testes de carga. O objetivo é fornecer uma base eficiente para sistemas de reserva de passagens aéreas, facilitando integrações e consultas rápidas.

## Descrição
Módulo A implementado em Python, responsável por gerenciar informações de voos e fornecer consultas via gRPC.

## Funcionalidades Implementadas

### Informações de Voos
- Origem, destino, data, preço
- Companhia aérea, número do voo, horário de partida e chegada
- Duração do voo, classe econômica, executiva, primeira
- Assentos disponíveis e status (ativo, cancelado, lotado)

### Métodos gRPC
- `ConsultarVoos`: Consulta voos disponíveis com filtros por:
  - Faixa de preço, companhia aérea, faixa de horário
  - Ordenação dos resultados (mais barato, mais rápido, menos escalas)

### Funcionalidades Especiais
- Alteração dinâmica de preços conforme proximidade da data
- Possibilidade de retorno "sem disponibilidade" em determinados voos
- Simula atraso no processamento (tempo de resposta entre 1-3s)
- Suporta testes de carga retornando grandes volumes de voos

## Como executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Gerar código gRPC
```bash
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. voos_service.proto
```

### 3. Executar servidor
```bash
python voos_server.py
```

### 4. Testar cliente
```bash
python voos_client.py
```

## Arquitetura
- **Servidor gRPC**: Porta 50051
- **Base de dados simulada**: 1000 voos gerados automaticamente
- **Filtros suportados**: origem, destino, data, preço, companhia, horário
- **Ordenação**: preço, horário, duração
- **Comportamento real**: atrasos, indisponibilidade, variação de preços

## Testes de Carga
O cliente inclui função de teste de carga que simula múltiplas requisições simultâneas para análise de desempenho.

## Documentação do Módulo A
Esta documentação se refere ao Módulo A do sistema de reserva de voos, detalhando suas funcionalidades, como executar o módulo e informações sobre sua arquitetura e testes de carga.

