const express = require('express');
const { getHotelClient } = require('../grpc/clients');
const router = express.Router();

router.post('/checkout', async (req, res) => {
  try {
    const { items } = req.body;

    if (!items || items.length === 0) {
      return res.status(400).json({ error: 'Carrinho vazio' });
    }

    const client = getHotelClient();

    const call = client.FinalizarCompra((error, response) => {
      if (error) {
        console.error('gRPC error:', error);
        return res.status(500).json({ error: 'Erro ao processar compra' });
      }

      res.json({
        sucesso: response.sucesso,
        codigo_confirmacao: response.codigo_confirmacao || response.codigoConfirmacao,
        valor_total: response.valor_total || response.valorTotal,
        total_itens: response.total_itens || response.totalItens,
        erros: response.erros || [],
        timestamp: response.timestamp
      });
    });

    items.forEach((item) => {
      call.write({
        tipo: item.tipo,
        id: item.id,
        detalhes: item.detalhes,
        preco: item.preco
      });
    });

    call.end();

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
