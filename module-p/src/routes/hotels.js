const express = require('express');
const { getHotelClient } = require('../grpc/clients');
const router = express.Router();

// Search hotels with filters
router.get('/search', async (req, res) => {
  try {
    const {
      city,
      min_stars,
      max_stars,
      min_price,
      max_price,
      accommodation_type,
      order_by = 'price',
      delay_seconds = 0
    } = req.query;

    const client = getHotelClient();
    
    const request = {
      city,
      min_stars: min_stars ? parseInt(min_stars) : undefined,
      max_stars: max_stars ? parseInt(max_stars) : undefined,
      min_price: min_price ? parseFloat(min_price) : undefined,
      max_price: max_price ? parseFloat(max_price) : undefined,
      accommodation_type,
      order_by,
      delay_seconds: parseInt(delay_seconds)
    };

    client.SearchHotels(request, (error, response) => {
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
