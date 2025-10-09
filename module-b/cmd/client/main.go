package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	pb "hotel-service/proto"
)

func main() {
	conn, err := grpc.Dial("localhost:50052", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("Não foi possível conectar: %v", err)
	}
	defer conn.Close()

	client := pb.NewHotelServiceClient(conn)

	// Teste 1: Buscar hotéis em São Paulo
	fmt.Println("=== Buscando hotéis em São Paulo ===")
	searchHotels(client, &pb.SearchHotelsRequest{
		City:     "São Paulo",
		MinStars: 3,
		MaxStars: 5,
		MinPrice: 100.0,
		MaxPrice: 500.0,
		OrderBy:  "price",
	})

	fmt.Println("\n" + "="*50 + "\n")

	// Teste 2: Buscar resorts no Rio de Janeiro
	fmt.Println("=== Buscando resorts no Rio de Janeiro ===")
	searchHotels(client, &pb.SearchHotelsRequest{
		City:              "Rio de Janeiro",
		MinStars:          4,
		MaxStars:          5,
		AccommodationType: "Resort",
		OrderBy:           "rating",
	})

	fmt.Println("\n" + "="*50 + "\n")

	// Teste 3: Teste de performance com delay
	fmt.Println("=== Teste de performance (delay 2s) ===")
	start := time.Now()
	searchHotels(client, &pb.SearchHotelsRequest{
		City:         "Brasília",
		MinStars:     1,
		MaxStars:     5,
		DelaySeconds: 2,
		OrderBy:      "price",
	})
	duration := time.Since(start)
	fmt.Printf("Tempo total de resposta: %v\n", duration)
}

func searchHotels(client pb.HotelServiceClient, req *pb.SearchHotelsRequest) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	resp, err := client.SearchHotels(ctx, req)
	if err != nil {
		log.Printf("Erro ao buscar hotéis: %v", err)
		return
	}

	fmt.Printf("Encontrados %d hotéis\n", len(resp.Hotels))
	fmt.Printf("Há disponibilidade: %v\n\n", resp.HasAvailability)

	for i, hotel := range resp.Hotels {
		fmt.Printf("Hotel %d:\n", i+1)
		fmt.Printf("  Nome: %s\n", hotel.Name)
		fmt.Printf("  Cidade: %s\n", hotel.City)
		fmt.Printf("  Estrelas: %d⭐\n", hotel.Stars)
		fmt.Printf("  Preço: R$ %.2f\n", hotel.Price)
		fmt.Printf("  Tipo: %s\n", hotel.AccommodationType)
		fmt.Printf("  Disponível: %v\n", hotel.Available)
		fmt.Printf("  Amenidades: %v\n", hotel.Amenities)
		fmt.Println()
	}
}