const { getFlightClient, getHotelClient } = require('../grpc/clients');

function setupChatWebSocket(wss) {
  wss.on('connection', (ws) => {
    console.log('Cliente conectado ao chat');

    const flightClient = getFlightClient();
    const hotelClient = getHotelClient();

    const flightStream = flightClient.ChatSuporte();
    const hotelStream = hotelClient.ChatSuporte();

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

    flightStream.on('error', (error) => {
      console.error('Flight chat stream error:', error);
    });

    hotelStream.on('error', (error) => {
      console.error('Hotel chat stream error:', error);
    });

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

    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data);
        const timestamp = new Date().toISOString();

        const mensagemLower = message.mensagem.toLowerCase();
        const isAboutPackage = /pacote|pacotes|combo/.test(mensagemLower);
        const isAboutFlight = /voo|voos|voar|aereo|aéreo|aviao|avião|passagem|passagens/.test(mensagemLower);
        const isAboutHotel = /hotel|hoteis|hotéis|hospedagem|quarto|quartos|pousada|resort|hostel/.test(mensagemLower);

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
          flightStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'voo'
          });
        } else if (isAboutHotel) {
          hotelStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'hotel'
          });
        } else {
          flightStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'geral'
          });
          hotelStream.write({
            usuario: 'cliente',
            mensagem: message.mensagem,
            timestamp: timestamp,
            contexto: 'geral'
          });
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    ws.on('close', () => {
      console.log('Cliente desconectado do chat');
      flightStream.end();
      hotelStream.end();
    });

    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });
}

module.exports = { setupChatWebSocket };
