const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const path = require('path');

const flightRoutes = require('./routes/flights');
const hotelRoutes = require('./routes/hotels');
const packageRoutes = require('./routes/packages');
const cartRoutes = require('./routes/cart');
const { setupChatWebSocket } = require('./websocket/chatHandler');

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

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, 
  max: 100 
});
app.use(limiter);

app.use('/api/flights', flightRoutes);
app.use('/api/hotels', hotelRoutes);
app.use('/api/packages', packageRoutes);
app.use('/api/cart', cartRoutes);

app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

setupChatWebSocket(wss);

server.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log(`WebSocket Chat available at /chat endpoint`);
});
