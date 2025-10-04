# Sistema de Reserva de Voos e Hotéis


Para tudo funcionar corretamente, você precisa garantir:

1. **Comunicação entre os módulos**  
   - O módulo P (API Gateway) deve conseguir se conectar via gRPC ao serviço de Voos (Python) e ao serviço de Hotéis (Go).
   - Certifique-se de que os serviços de Voos e Hotéis estejam rodando e escutando nas portas corretas.

2. **Compatibilidade dos protos**  
   - Os arquivos `.proto` usados pelo módulo P devem ser compatíveis com os serviços de Voos e Hotéis.  
   - Verifique se os métodos, mensagens e campos dos protos estão iguais nos três módulos.

3. **Configuração de endpoints**  
   - No módulo P, configure corretamente os endereços/ports dos serviços de Voos e Hotéis em `grpc/clients.js`.

4. **Testes de integração**  
   - Faça testes de ponta a ponta: envie uma requisição REST ao módulo P e veja se ele retorna o pacote de viagem corretamente (consultando ambos os serviços).

5. **Tratamento de erros**  
   - Implemente tratamento de erros para falhas de conexão, respostas inválidas ou serviços fora do ar.

6. **Documentação e exemplos de uso**  
   - Tenha exemplos de requisições REST para o módulo P e instruções de como subir todos os serviços (Python, Go, Node.js).

7. **(Opcional) Orquestração com Kubernetes**  
   - Se for simular em Minikube, crie os manifests (`Deployment`, `Service`) para cada módulo.

Se todos esses pontos estiverem ok, o sistema deve funcionar conforme o esperado!