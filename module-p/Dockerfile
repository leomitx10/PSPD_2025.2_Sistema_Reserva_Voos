FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --production

COPY src ./src
COPY public ./public

EXPOSE 3000

ENV FLIGHT_SERVICE_HOST=localhost
ENV FLIGHT_SERVICE_PORT=50051
ENV HOTEL_SERVICE_HOST=localhost
ENV HOTEL_SERVICE_PORT=50052

CMD ["node", "src/server.js"]
