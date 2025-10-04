const express = require('express');
const { getFlightClient, getHotelClient } = require('../grpc/clients');
const router = express.Router();

// Search travel packages (flight + hotel)
router.get('/search', async (req, res) => {
  try {
    const {
      origin,
      destination,
      departure_date,
      return_date,
      passengers = 1
    } = req.query;

    const flightClient = getFlightClient();
    const hotelClient = getHotelClient();

    // Search flights and hotels in parallel
    const promises = [
      new Promise((resolve, reject) => {
        flightClient.ConsultarVoos({
          origem: origin,
          destino: destination,
          data: departure_date
        }, (error, response) => {
          if (error) reject(error);
          else resolve(response);
        });
      }),
      new Promise((resolve, reject) => {
        hotelClient.SearchHotels({
          city: destination
        }, (error, response) => {
          if (error) reject(error);
          else resolve(response);
        });
      })
    ];

    const [flightResults, hotelResults] = await Promise.all(promises);

    // Combine results into packages
    const packages = [];
    const flights = flightResults.voos || [];
    const hotels = hotelResults.hotels || [];
    
    flights.forEach(flight => {
      hotels.forEach(hotel => {
        packages.push({
          id: `${flight.id}-${hotel.id}`,
          flight,
          hotel,
          total_price: flight.preco + hotel.price,
          savings: (flight.preco + hotel.price) * 0.1 // 10% package discount
        });
      });
    });

    // Sort by total price
    packages.sort((a, b) => a.total_price - b.total_price);

    res.json({
      packages: packages.slice(0, 20), // Limit to 20 packages
      total_count: packages.length
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
