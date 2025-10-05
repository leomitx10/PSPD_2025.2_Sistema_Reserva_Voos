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

        // Calculate check-in and check-out based on flight dates
        const checkin = data || flight.data; // Use flight departure date as check-in
        let checkout = data_volta;

        // If no return date, calculate checkout as checkin + 3 days
        if (!checkout && checkin) {
          const checkinDate = new Date(checkin);
          checkinDate.setDate(checkinDate.getDate() + 3);
          checkout = checkinDate.toISOString().split('T')[0];
        }

        // Calculate number of nights
        const nights = checkout && checkin ?
          Math.ceil((new Date(checkout) - new Date(checkin)) / (1000 * 60 * 60 * 24)) : 1;

        // Calculate total price (flight + hotel per night * nights)
        const totalPrice = flight.preco + (hotel.price * nights);

        // Apply budget filter if specified
        if (!max_budget || totalPrice <= max_budget) {
          // Add data_volta, check-in, check-out to flight
          const flightWithDates = {
            ...flight,
            data_volta: data_volta || checkout,
            checkin: checkin,
            checkout: checkout
          };

          packages.push({
            flight: flightWithDates,
            hotel: { ...hotel, checkin, checkout, nights },
            total_price: totalPrice,
            nights: nights
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
