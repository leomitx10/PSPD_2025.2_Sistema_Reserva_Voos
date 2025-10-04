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

// Client instances pointing to correct ports
const flightClient = new voosProto.VoosService('localhost:50051', grpc.credentials.createInsecure());
const hotelClient = new hotelProto.HotelService('localhost:50052', grpc.credentials.createInsecure());

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
