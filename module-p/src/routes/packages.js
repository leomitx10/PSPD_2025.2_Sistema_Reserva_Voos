const express = require('express');
const { getFlightClient, getHotelClient } = require('../grpc/clients');
const router = express.Router();

// Search travel packages (flight + hotel)
router.post('/search', async (req, res) => {
  try {
    const {
      origem,
      destino,
      data,
      data_volta,
      rooms = 1,
      guests = 1,
      flight_class,
      min_rating,
      max_budget,
      datas_flexiveis = false
    } = req.body;

    const flightClient = getFlightClient();
    const hotelClient = getHotelClient();

    // Search flights and hotels in parallel
    const promises = [
      new Promise((resolve, reject) => {
        flightClient.ConsultarVoos({
          origem: origem,
          destino: destino,
          data: datas_flexiveis ? '' : data,
          ordenacao: 'preco'
        }, (error, response) => {
          if (error) reject(error);
          else resolve(response);
        });
      }),
      new Promise((resolve, reject) => {
        hotelClient.SearchHotels({
          city: destino,
          min_stars: min_rating ? parseInt(min_rating) : undefined,
          order_by: 'price'
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

    // Limit combinations
    const maxFlights = Math.min(flights.length, 5);
    const maxHotels = Math.min(hotels.length, 5);

    for (let i = 0; i < maxFlights; i++) {
      for (let j = 0; j < maxHotels; j++) {
        const flight = flights[i];
        const hotel = hotels[j];
        const totalPrice = flight.preco + hotel.price;

        // Apply budget filter if specified
        if (!max_budget || totalPrice <= max_budget) {
          packages.push({
            flight,
            hotel,
            total_price: totalPrice
          });
        }
      }
    }

    // Sort by total price
    packages.sort((a, b) => a.total_price - b.total_price);

    res.json({
      packages: packages.slice(0, 10)
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
