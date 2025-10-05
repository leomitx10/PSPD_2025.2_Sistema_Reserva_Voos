package service

import (
	"context"
	"fmt"
	"io"
	"strings"
	"time"

	pb "hotel-service/proto"
	"hotel-service/internal/models"
)

type HotelServiceServer struct {
	pb.UnimplementedHotelServiceServer
	repository *models.HotelRepository
}

func NewHotelServiceServer() *HotelServiceServer {
	return &HotelServiceServer{
		repository: models.NewHotelRepository(),
	}
}

func (s *HotelServiceServer) SearchHotels(ctx context.Context, req *pb.SearchHotelsRequest) (*pb.SearchHotelsResponse, error) {
	// Simulate processing delay for performance testing
	if req.DelaySeconds > 0 {
		time.Sleep(time.Duration(req.DelaySeconds) * time.Second)
	}
	
	hotels := s.repository.SearchHotels(
		req.City,
		req.MinStars,
		req.MaxStars,
		req.MinPrice,
		req.MaxPrice,
		req.AccommodationType,
		req.OrderBy,
	)
	
	// Convert to protobuf format
	pbHotels := make([]*pb.Hotel, 0, len(hotels))
	hasAvailability := false
	
	for _, hotel := range hotels {
		if hotel.Available {
			hasAvailability = true
		}
		
		pbHotels = append(pbHotels, &pb.Hotel{
			Id:                hotel.ID,
			Name:              hotel.Name,
			City:              hotel.City,
			Stars:             hotel.Stars,
			Price:             hotel.BasePrice,
			Available:         hotel.Available,
			Amenities:         hotel.Amenities,
			AccommodationType: hotel.AccommodationType,
		})
	}
	
	return &pb.SearchHotelsResponse{
		Hotels:        pbHotels,
		HasAvailability: hasAvailability,
	}, nil
}

// FinalizarCompra implements Client Streaming RPC
// Receives multiple cart items and processes them as a single transaction
func (s *HotelServiceServer) FinalizarCompra(stream pb.HotelService_FinalizarCompraServer) error {
	var itens []*pb.ItemCarrinho
	var valorTotal float64

	fmt.Println("[FINALIZAR COMPRA] Recebendo itens do carrinho...")

	// Receive all items from client stream
	for {
		item, err := stream.Recv()
		if err == io.EOF {
			// Client finished sending items
			break
		}
		if err != nil {
			return err
		}

		itens = append(itens, item)
		valorTotal += item.Preco
		fmt.Printf("[FINALIZAR COMPRA] Recebido: %s - %s (R$ %.2f)\n", item.Tipo, item.Id, item.Preco)
	}

	// Process the purchase
	time.Sleep(1 * time.Second) // Simulate payment processing

	codigoConfirmacao := fmt.Sprintf("PKG%d%02d%02d", time.Now().Unix()%10000, len(itens), int(valorTotal)%100)

	fmt.Printf("[FINALIZAR COMPRA] Processando %d itens - Total: R$ %.2f\n", len(itens), valorTotal)

	// Send single response
	resposta := &pb.RespostaCompra{
		Sucesso:            true,
		CodigoConfirmacao:  codigoConfirmacao,
		ValorTotal:         valorTotal,
		TotalItens:         int32(len(itens)),
		Erros:              []string{},
		Timestamp:          time.Now().Format("2006-01-02 15:04:05"),
	}

	fmt.Printf("[FINALIZAR COMPRA] ✅ Confirmado! Código: %s\n", codigoConfirmacao)

	return stream.SendAndClose(resposta)
}

// ChatSuporte implements Bidirectional Streaming RPC
// Handles chat support for hotel-related questions
func (s *HotelServiceServer) ChatSuporte(stream pb.HotelService_ChatSuporteServer) error {
	fmt.Println("[CHAT SUPORTE HOTÉIS] Chat iniciado")

	for {
		mensagem, err := stream.Recv()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return err
		}

		fmt.Printf("[CHAT HOTÉIS] Recebido: %s\n", mensagem.Mensagem)

		// Detect if message is about hotels, packages or general
		palavrasHotel := []string{"hotel", "hoteis", "hotéis", "hospedagem", "quarto", "quartos", "pousada", "resort", "hostel"}
		palavrasPacote := []string{"pacote", "pacotes", "combo"}
		palavrasVoo := []string{"voo", "voos", "voar", "aereo", "aéreo", "aviao", "avião", "passagem", "passagens"}
		mensagemLower := strings.ToLower(mensagem.Mensagem)
		contexto := mensagem.Contexto

		// Check about what
		isAboutHotel := false
		isAboutPackage := false
		isAboutFlight := false

		for _, palavra := range palavrasHotel {
			if strings.Contains(mensagemLower, palavra) {
				isAboutHotel = true
				break
			}
		}

		for _, palavra := range palavrasPacote {
			if strings.Contains(mensagemLower, palavra) {
				isAboutPackage = true
				break
			}
		}

		for _, palavra := range palavrasVoo {
			if strings.Contains(mensagemLower, palavra) {
				isAboutFlight = true
				break
			}
		}

		// Respond if about hotels, packages OR general message (no specific keyword and not about flights)
		isGeneral := contexto == "geral" || (!isAboutHotel && !isAboutPackage && !isAboutFlight && contexto != "voo")

		if isAboutHotel || isAboutPackage || isGeneral {
			time.Sleep(500 * time.Millisecond) // Simulate processing

			var resposta string

			// Generate contextual response
			if isAboutPackage {
				resposta = "🏨 HOTÉIS - Nossos pacotes incluem hospedagens confortáveis em hotéis, pousadas e resorts! A partir de R$ 80/noite com até 30% de desconto."
			} else if isGeneral {
				resposta = "🏨 HOTÉIS - Posso te ajudar com informações sobre hospedagens! Temos hotéis, pousadas, resorts e hostels."
			} else if strings.Contains(mensagemLower, "preco") || strings.Contains(mensagemLower, "preço") || strings.Contains(mensagemLower, "barato") {
				resposta = "💰 Temos hotéis a partir de R$ 80/noite! Use os filtros de preço para encontrar as melhores ofertas."
			} else if strings.Contains(mensagemLower, "estrela") || strings.Contains(mensagemLower, "avaliacao") || strings.Contains(mensagemLower, "avaliação") {
				resposta = "⭐ Oferecemos hotéis de 1 a 5 estrelas. Hotéis 4 e 5 estrelas têm as melhores avaliações!"
			} else if strings.Contains(mensagemLower, "comodidade") || strings.Contains(mensagemLower, "amenidade") {
				resposta = "🏊 Nossos hotéis oferecem: Wi-Fi, Piscina, Academia, Spa, Restaurante, Estacionamento, Café da Manhã e Ar Condicionado."
			} else if strings.Contains(mensagemLower, "tipo") {
				resposta = "🏨 Temos 4 tipos de acomodação: Hotel, Pousada, Resort e Hostel. Qual você prefere?"
			} else if strings.Contains(mensagemLower, "cidade") || strings.Contains(mensagemLower, "destino") {
				resposta = "🌆 Temos hotéis em: São Paulo, Rio de Janeiro, Brasília, Salvador, Fortaleza, Belo Horizonte, Recife, Manaus e Porto Alegre."
			} else {
				resposta = "🏨 Olá! Como posso ajudar com informações sobre hotéis? Temos diversas opções de hospedagem!"
			}

			// Send response
			err = stream.Send(&pb.ChatMessage{
				Usuario:   "suporte",
				Mensagem:  resposta,
				Timestamp: time.Now().Format("2006-01-02 15:04:05"),
				Contexto:  "hotel",
			})

			if err != nil {
				return err
			}

			fmt.Printf("[CHAT HOTÉIS] Respondido: %s\n", resposta)
		} else {
			// Not about hotels, ignore (let flight module handle it)
			fmt.Println("[CHAT HOTÉIS] Mensagem não é sobre hotéis, ignorando...")
		}
	}
}
