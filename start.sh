#!/bin/bash

# Script de início rápido para o Sistema de Reserva de Voos
# Autor: Leandro (@leomitx10)

set -e

echo "🚀 Sistema de Reserva de Voos - Início Rápido"
echo "============================================="

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "Voos" ] || [ ! -d "hotel-service" ]; then
    echo "❌ Erro: Execute este script do diretório raiz do projeto"
    exit 1
fi

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo "🔍 Verificando dependências..."

if ! command_exists go; then
    echo "❌ Go não está instalado. Instale com: sudo apt install golang-go"
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python3 não está instalado. Instale com: sudo apt install python3 python3-pip"
    exit 1
fi

if ! command_exists protoc; then
    echo "❌ Protocol Buffers não está instalado. Instale com: sudo apt install protobuf-compiler"
    exit 1
fi

echo "✅ Todas as dependências básicas estão instaladas"

# Verificar plugins Go
echo "🔧 Verificando plugins Go para protoc..."
if ! command_exists protoc-gen-go; then
    echo "📦 Instalando protoc-gen-go..."
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
fi

if ! command_exists protoc-gen-go-grpc; then
    echo "📦 Instalando protoc-gen-go-grpc..."
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
fi

# Configurar PATH
export PATH="$PATH:$(go env GOPATH)/bin"

echo "✅ Plugins Go configurados"

# Preparar Hotel Service
echo "🏨 Preparando Hotel Service..."
cd hotel-service

echo "📦 Instalando dependências Go..."
go mod tidy
go mod download

echo "🔨 Gerando código protobuf..."
make proto

echo "✅ Hotel Service preparado"
cd ..

# Preparar Voos Service
echo "🛫 Preparando Voos Service..."
cd Voos

echo "📦 Instalando dependências Python..."
pip3 install -r requirements.txt

echo "✅ Voos Service preparado"
cd ..

echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "Para executar os serviços:"
echo ""
echo "📱 Terminal 1 - Serviço de Voos:"
echo "   cd Voos && python3 voos_server.py"
echo ""
echo "📱 Terminal 2 - Serviço de Hotéis:"
echo "   cd hotel-service && make run"
echo ""
echo "📱 Terminal 3 - Teste (opcional):"
echo "   cd Voos && python3 voos_client.py"
echo ""
echo "🌐 Portas dos serviços:"
echo "   - Voos: localhost:50051"
echo "   - Hotéis: localhost:50052"
echo ""