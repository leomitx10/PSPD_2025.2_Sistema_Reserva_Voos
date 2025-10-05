FROM python:3.9-slim

WORKDIR /app

# Configurar Python para modo unbuffered (logs aparecem imediatamente)
ENV PYTHONUNBUFFERED=1

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar estrutura do projeto
COPY proto/ proto/
COPY cmd/ cmd/
COPY internal/ internal/

# Gerar arquivos proto no build
RUN python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto proto/voos_service.proto

# Expor porta gRPC
EXPOSE 50051

# Iniciar servidor com output unbuffered
CMD ["python", "-u", "cmd/server/main.py"]
