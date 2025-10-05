FROM python:3.9-slim

WORKDIR /app

# Configurar Python para modo unbuffered (logs aparecem imediatamente)
ENV PYTHONUNBUFFERED=1

# Instalar dependências primeiro
RUN pip install --no-cache-dir grpcio grpcio-tools

# Copiar arquivos
COPY voos_service.proto .
COPY voos_server.py .

# Gerar arquivos proto no build
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. voos_service.proto

# Expor porta gRPC
EXPOSE 50051

# Iniciar servidor com output unbuffered
CMD ["python", "-u", "voos_server.py"]
