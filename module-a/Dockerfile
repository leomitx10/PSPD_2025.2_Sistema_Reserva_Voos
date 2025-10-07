FROM python:3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ proto/
COPY cmd/ cmd/
COPY internal/ internal/

RUN python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto proto/voos_service.proto

EXPOSE 50051

CMD ["python", "-u", "cmd/server/main.py"]
