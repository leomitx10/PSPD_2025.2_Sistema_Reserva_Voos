FROM golang:1.21-alpine AS builder

WORKDIR /app

# Instalar protoc e plugins Go
RUN apk add --no-cache protobuf protobuf-dev
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.1
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2.0

# Copiar arquivos de dependência
COPY go.mod ./
RUN go mod download

# Copiar código fonte
COPY . .

# Atualizar dependências
RUN go mod tidy

# Recompilar proto files
RUN protoc --go_out=. --go-grpc_out=. proto/hotel.proto

# Build da aplicação
RUN CGO_ENABLED=0 GOOS=linux go build -o hotel-server ./cmd/server

# Imagem final
FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/hotel-server .

# Expor portas gRPC e métricas
EXPOSE 50052 8001

# Iniciar servidor
CMD ["./hotel-server"]
