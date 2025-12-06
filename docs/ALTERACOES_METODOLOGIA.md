# Alterações Metodológicas para Testes de Carga

**Data**: 05 de dezembro de 2025  
**Contexto**: Configurações ajustadas para permitir testes de carga adequados

---

## 1. Alteração no Rate Limiter do API Gateway

### 1.1 Descrição da Alteração

O rate limiter do API Gateway foi **desabilitado** durante a execução dos testes de carga.

**Arquivo Modificado**: `module-p/src/server.js`

### 1.2 Código Original

```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutos
  max: 100                    // Máximo 100 requisições
});
app.use(limiter);
```

### 1.3 Código Modificado

```javascript
// Rate limiter desabilitado para testes de carga
// Conforme metodologia documentada no relatório
// const limiter = rateLimit({
//   windowMs: 15 * 60 * 1000, 
//   max: 10000
// });
// app.use(limiter);
```

### 1.4 Justificativa

#### Problema Identificado

Durante os testes iniciais, observou-se que:
- **97% das requisições falhavam** com status 429 (Too Many Requests)
- O limite de 100 requisições/15 minutos era atingido em **segundos**
- Impossibilidade de medir performance real da aplicação
- HPA não podia ser testado adequadamente pois a limitação era artificial

#### Exemplo de Falhas Observadas

```
Teste com 20 usuários por 90 segundos:
- Total de requisições: 3027
- Falhas por 429: 2930 (96.80%)
- Taxa de requisições: 33.70 req/s
- Limite atingido em: ~3 segundos
```

#### Necessidade da Mudança

Para atender aos objetivos do projeto, era necessário:
1. Medir **throughput real** da aplicação
2. Identificar **gargalos reais** (CPU, memória, I/O de rede)
3. Testar **autoscaling (HPA)** sob carga crescente
4. Comparar **diferentes configurações** de forma justa

### 1.5 Impactos

#### Impactos Positivos ✅

1. **Testes de Carga Válidos**
   - Permite executar cenários com 50-200 usuários simultâneos
   - Mede latência e throughput reais
   - Identifica limites de CPU/memória dos pods

2. **HPA Funcional**
   - Autoscaling pode ser testado adequadamente
   - Métricas de CPU/memória refletem carga real
   - Comportamento de scale-up/scale-down observável

3. **Observabilidade Adequada**
   - Prometheus coleta métricas realistas
   - Queries PromQL retornam dados úteis
   - Dashboards mostram comportamento real

4. **Comparações Justas**
   - Cenários podem ser comparados sem viés
   - Infraestrutura é o fator limitante, não configuração artificial

#### Riscos e Mitigações ⚠️

| Risco | Mitigação |
|-------|-----------|
| Aplicação sem proteção em produção | Reativar rate limiter em ambientes não-teste |
| Sobrecarga acidental do sistema | Executar testes em ambiente isolado |
| Falta de documentação | Documentar claramente no relatório e código |

### 1.6 Conformidade com Especificação

A especificação do projeto permite alterações para facilitar observabilidade:

> **Observações**: Embora a aplicação a ser entregue deva ser a mesma que foi desenvolvida no trabalho extraclasse, **eventuais alterações necessárias para facilitar a observabilidade e monitoramento da aplicação são admitidos**, desde que estejam documentados no relatório de entrega.

**Verificação de Conformidade**:
- ✅ Alteração documentada no relatório (Seção 3.8)
- ✅ Não altera arquitetura P-A-B com gRPC
- ✅ Facilita observabilidade e monitoramento
- ✅ Justificativa técnica clara
- ✅ Riscos identificados e mitigados

### 1.7 Validação da Alteração

Teste realizado após a mudança:

```bash
Testando sem rate limiter...
✓ 50 requisições - Sucesso: 50, Falhas 429: 0
✓ 100 requisições - Sucesso: 100, Falhas 429: 0
✓ 150 requisições - Sucesso: 150, Falhas 429: 0

Resultado final: 150 sucessos, 0 falhas 429 de 150 requisições
✅ Rate limiter desabilitado com sucesso!
```

**Conclusão**: Sistema agora aceita requisições sem limitação artificial, permitindo testes de carga adequados.

---

## 2. Recomendações para Produção

### 2.1 Reativar Rate Limiter

Em ambiente de produção, **reativar** o rate limiter com limites apropriados:

```javascript
const limiter = rateLimit({
  windowMs: 1 * 60 * 1000,     // 1 minuto
  max: 100,                     // 100 requisições por minuto por IP
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      error: 'Too many requests',
      retryAfter: req.rateLimit.resetTime
    });
  }
});
app.use('/api/', limiter);
```

### 2.2 Alternativas de Rate Limiting

Para ambientes de produção mais robustos, considerar:

1. **API Gateway Dedicado**
   - Kong
   - Nginx Ingress Controller
   - AWS API Gateway
   - Azure API Management

2. **Rate Limiting por Usuário/API Key**
   ```javascript
   const limiter = rateLimit({
     keyGenerator: (req) => req.headers['x-api-key'] || req.ip,
     max: 1000  // Limite maior para usuários autenticados
   });
   ```

3. **Rate Limiting no Ingress (Kubernetes)**
   ```yaml
   nginx.ingress.kubernetes.io/limit-rps: "100"
   nginx.ingress.kubernetes.io/limit-connections: "50"
   ```

### 2.3 Monitoramento de Rate Limiting

Adicionar métricas Prometheus:

```javascript
const rateLimitCounter = new promClient.Counter({
  name: 'api_rate_limit_hits_total',
  help: 'Total de requisições bloqueadas por rate limit'
});

// No handler do rate limiter
handler: (req, res) => {
  rateLimitCounter.inc();
  res.status(429).json({ error: 'Too many requests' });
}
```

---

## 3. Checklist de Conformidade

- [x] Alteração documentada no relatório final
- [x] Justificativa técnica clara
- [x] Código comentado no fonte
- [x] Testes de validação realizados
- [x] Riscos identificados
- [x] Mitigações propostas
- [x] Recomendações para produção
- [x] Conformidade com especificação verificada

---

## 4. Referências

- Especificação do Projeto PSPD 2025.2
- Express Rate Limit Documentation: https://github.com/express-rate-limit/express-rate-limit
- Cloud Native DevOps with Kubernetes, Cap. 15-16
- Best Practices for API Rate Limiting: https://cloud.google.com/architecture/rate-limiting-strategies-techniques

---

**Observação Final**: Esta alteração é **temporária** e específica para o ambiente de testes. Em produção, rate limiting adequado é **essencial** para proteção contra abuso e garantia de disponibilidade do serviço.
