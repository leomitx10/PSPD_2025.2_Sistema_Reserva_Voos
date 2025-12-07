package main

import (
	"log"
	"net"
	"net/http"
	"strings"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"hotel-service/internal/service"
	pb "hotel-service/proto"
)

func main() {
	// Iniciar servidor HTTP para métricas Prometheus na porta 8001
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		log.Println("📊 Servidor de métricas Prometheus rodando na porta 8001")
		if err := http.ListenAndServe(":8001", nil); err != nil {
			log.Fatalf("Failed to start metrics server: %v", err)
		}
	}()

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
