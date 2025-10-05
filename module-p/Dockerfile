FROM node:18-alpine

WORKDIR /app

# Copiar package.json
COPY package*.json ./

# Instalar dependências
RUN npm install --production

# Copiar código fonte
COPY src ./src
COPY public ./public

# Expor porta HTTP
EXPOSE 3000

# Variáveis de ambiente para conectar aos serviços
ENV FLIGHT_SERVICE_HOST=localhost
ENV FLIGHT_SERVICE_PORT=50051
ENV HOTEL_SERVICE_HOST=localhost
ENV HOTEL_SERVICE_PORT=50052

# Iniciar servidor
CMD ["node", "src/server.js"]
