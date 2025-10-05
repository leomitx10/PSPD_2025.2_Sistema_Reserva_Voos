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

// Middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable for development
}));
app.use(cors());
app.use(compression());
app.use(express.json());

// Serve static files (Frontend)
app.use(express.static(path.join(__dirname, '../public')));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Routes
app.use('/api/flights', flightRoutes);
app.use('/api/hotels', hotelRoutes);
app.use('/api/packages', packageRoutes);
app.use('/api/cart', cartRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

// Setup WebSocket for chat
setupChatWebSocket(wss);

server.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log(`WebSocket Chat available at ws://localhost:${PORT}/chat`);
});
