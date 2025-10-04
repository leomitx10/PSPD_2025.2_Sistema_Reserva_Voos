package service

import (
	"context"
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
