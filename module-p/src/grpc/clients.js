const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// Load proto files
const flightProtoPath = path.join(__dirname, '../protos/flights.proto');
const hotelProtoPath = path.join(__dirname, '../protos/hotels.proto');

const flightPackageDefinition = protoLoader.loadSync(flightProtoPath, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const hotelPackageDefinition = protoLoader.loadSync(hotelProtoPath, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const voosProto = grpc.loadPackageDefinition(flightPackageDefinition).voos;
const hotelProto = grpc.loadPackageDefinition(hotelPackageDefinition).hotel;

// Get service hosts from environment variables (for Docker) or use localhost
const FLIGHT_SERVICE_HOST = process.env.FLIGHT_SERVICE_HOST || 'localhost';
const FLIGHT_SERVICE_PORT = process.env.FLIGHT_SERVICE_PORT || '50051';
const HOTEL_SERVICE_HOST = process.env.HOTEL_SERVICE_HOST || 'localhost';
const HOTEL_SERVICE_PORT = process.env.HOTEL_SERVICE_PORT || '50052';

// Client instances pointing to correct ports
const flightClient = new voosProto.VoosService(
  `${FLIGHT_SERVICE_HOST}:${FLIGHT_SERVICE_PORT}`,
  grpc.credentials.createInsecure()
);
const hotelClient = new hotelProto.HotelService(
  `${HOTEL_SERVICE_HOST}:${HOTEL_SERVICE_PORT}`,
  grpc.credentials.createInsecure()
);

console.log(`Flight Service: ${FLIGHT_SERVICE_HOST}:${FLIGHT_SERVICE_PORT}`);
console.log(`Hotel Service: ${HOTEL_SERVICE_HOST}:${HOTEL_SERVICE_PORT}`);

function getFlightClient() {
  return flightClient;
}

function getHotelClient() {
  return hotelClient;
}

module.exports = {
  getFlightClient,
  getHotelClient
};
