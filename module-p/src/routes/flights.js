const express = require('express');
const { getFlightClient } = require('../grpc/clients');
const router = express.Router();

router.post('/search', async (req, res) => {
  try {
    const {
      origem,
      destino,
      data,
      data_volta,
      preco_max,
      companhia_aerea,
      faixa_horario,
      ordenacao = 'preco',
      classe,
      passageiros = 1,
      tipo_viagem = 'oneway',
      datas_flexiveis = false
    } = req.body;

    const client = getFlightClient();

    const request = {
      origem,
      destino,
      data: datas_flexiveis ? '' : data,
      preco_max: preco_max ? parseFloat(preco_max) : 0,
      companhia_aerea,
      faixa_horario,
      ordenacao
    };

    client.ConsultarVoos(request, (error, response) => {
      if (error) {
        console.error('gRPC error:', error);
        return res.status(500).json({ error: 'Service unavailable' });
      }

      if (data_volta && response.voos) {
        response.voos = response.voos.map(voo => ({
          ...voo,
          data_volta: data_volta
        }));
      }

      res.json(response);
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/monitor/:numeroVoo', (req, res) => {
  const { numeroVoo } = req.params;

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const client = getFlightClient();

  const call = client.MonitorarVoo({ numero_voo: numeroVoo });

  call.on('data', (update) => {
    res.write(`data: ${JSON.stringify({
      numero_voo: update.numero_voo,
      status: update.status,
      mensagem: update.mensagem,
      timestamp: update.timestamp,
      progresso_percentual: update.progresso_percentual
    })}\n\n`);
  });

  call.on('end', () => {
    res.end();
  });

  call.on('error', (error) => {
    console.error('Stream error:', error);
    res.write(`data: ${JSON.stringify({ error: 'Erro no monitoramento' })}\n\n`);
    res.end();
  });

  req.on('close', () => {
    call.cancel();
  });
});

module.exports = router;
