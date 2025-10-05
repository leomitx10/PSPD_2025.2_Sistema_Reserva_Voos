const { getFlightClient, getHotelClient } = require('../grpc/clients');

function setupChatWebSocket(wss) {
  wss.on('connection', (ws) => {
    console.log('Cliente conectado ao chat');

    const flightClient = getFlightClient();
    const hotelClient = getHotelClient();

    // Create bidirectional streams for both services
    const flightStream = flightClient.ChatSuporte();
    const hotelStream = hotelClient.ChatSuporte();

    // Handle messages from flight service
    flightStream.on('data', (message) => {
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify({
          usuario: message.usuario,
          mensagem: message.mensagem,
          timestamp: message.timestamp,
          contexto: message.contexto || 'voo'
        }));
      }
    });

    // Handle messages from hotel service
    hotelStream.on('data', (message) => {
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify({
          usuario: message.usuario,
          mensagem: message.mensagem,
          timestamp: message.timestamp,
          contexto: message.contexto || 'hotel'
        }));
      }
    });

    // Handle errors
    flightStream.on('error', (error) => {
      console.error('Flight chat stream error:', error);
    });

    hotelStream.on('error', (error) => {
      console.error('Hotel chat stream error:', error);
    });

    // Send welcome message
    setTimeout(() => {
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify({
          usuario: 'suporte',
          mensagem: 'Olá! Como posso ajudar você hoje? Posso ajudar com voos, hotéis ou pacotes.',
          timestamp: new Date().toISOString(),
          contexto: 'geral'
        }));
      }
    }, 500);

    // Handle messages from client
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data);
        const timestamp = new Date().toISOString();

        // Detect context based on keywords
        const mensagemLower = message.mensagem.toLowerCase();
        const isAboutPackage = /pacote|pacotes|combo/.test(mensagemLower);
        const isAboutFlight = /voo|voos|voar|aereo|aéreo|aviao|avião|passagem|passagens/.test(mensagemLower);
        const isAboutHotel = /hotel|hoteis|hotéis|hospedagem|quarto|quartos|pousada|resort|hostel/.test(mensagemLower);

        // If about packages, ALWAYS send to both services
        if (isAboutPackage) {
          flightStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'pacote'
          });
          hotelStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'pacote'
          });
        } else if (isAboutFlight) {
          // Only about flights
          flightStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'voo'
          });
        } else if (isAboutHotel) {
          // Only about hotels
          hotelStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'hotel'
          });
        } else {
          // Generic message - send help text
          setTimeout(() => {
            if (ws.readyState === ws.OPEN) {
              ws.send(JSON.stringify({
                usuario: 'suporte',
                mensagem: 'Posso ajudar com informações sobre voos, hotéis ou pacotes. Sobre qual desses você gostaria de saber mais?',
                timestamp: new Date().toISOString(),
                contexto: 'geral'
              }));
            }
          }, 500);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    // Handle client disconnect
    ws.on('close', () => {
      console.log('Cliente desconectado do chat');
      flightStream.end();
      hotelStream.end();
    });

    // Handle errors
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });
}

module.exports = { setupChatWebSocket };
