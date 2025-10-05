package main

import (
	"log"
	"net"
	"strings"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	"hotel-service/internal/service"
	pb "hotel-service/proto"
)

func main() {
	lis, err := net.Listen("tcp", ":50052")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	s := grpc.NewServer()
	hotelService := service.NewHotelServiceServer()

	pb.RegisterHotelServiceServer(s, hotelService)
	reflection.Register(s)

	log.Println(strings.Repeat("=", 60))
	log.Println("Hotel Service running on port 50052...")
	log.Println("Pressione Ctrl+C para parar")
	log.Println(strings.Repeat("=", 60))

	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
