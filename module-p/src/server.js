const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const path = require('path');
const promClient = require('prom-client');

const flightRoutes = require('./routes/flights');
const hotelRoutes = require('./routes/hotels');
const packageRoutes = require('./routes/packages');
const cartRoutes = require('./routes/cart');
const { setupChatWebSocket } = require('./websocket/chatHandler');

// Configuração do Prometheus
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// Métricas customizadas
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register]
});

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register]
});

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/chat' });

const PORT = process.env.PORT || 3000;

app.use(helmet({
  contentSecurityPolicy: false, 
}));
app.use(cors());
app.use(compression());
app.use(express.json());

app.use(express.static(path.join(__dirname, '../public')));

// Middleware para coletar métricas HTTP
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration.labels(req.method, req.route?.path || req.path, res.statusCode).observe(duration);
    httpRequestTotal.labels(req.method, req.route?.path || req.path, res.statusCode).inc();
  });
  
  next();
});

// Rate limiter desabilitado para testes de carga
// Conforme metodologia documentada no relatório
// const limiter = rateLimit({
//   windowMs: 15 * 60 * 1000, 
//   max: 10000
// });
// app.use(limiter);

app.use('/api/flights', flightRoutes);
app.use('/api/hotels', hotelRoutes);
app.use('/api/packages', packageRoutes);
app.use('/api/cart', cartRoutes);

app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Endpoint de métricas do Prometheus
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

setupChatWebSocket(wss);

server.listen(PORT, () => {
  console.log(`🚀 API Gateway rodando na porta ${PORT}`);
  console.log(`📊 Métricas disponíveis em http://localhost:${PORT}/metrics`);
  console.log(`💬 WebSocket Chat disponível em /chat`);
});
