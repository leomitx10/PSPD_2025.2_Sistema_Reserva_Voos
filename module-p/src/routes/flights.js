const express = require('express');
const { getFlightClient } = require('../grpc/clients');
const router = express.Router();

// Search flights with filters
router.get('/search', async (req, res) => {
  try {
    const {
      origem,
      destino,
      data,
      preco_max,
      companhia_aerea,
      faixa_horario,
      ordenacao = 'preco'
    } = req.query;

    const client = getFlightClient();
    
    const request = {
      origem,
      destino,
      data,
      preco_max: preco_max ? parseFloat(preco_max) : undefined,
      companhia_aerea,
      faixa_horario,
      ordenacao
    };

    client.ConsultarVoos(request, (error, response) => {
      if (error) {
        console.error('gRPC error:', error);
        return res.status(500).json({ error: 'Service unavailable' });
      }
      res.json(response);
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
