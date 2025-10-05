package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"hotel-service/internal/models"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
)

type SearchRequest struct {
	City               string  `json:"city"`
	MinStars           int32   `json:"min_stars"`
	MaxStars           int32   `json:"max_stars"`
	MinPrice           float64 `json:"min_price"`
	MaxPrice           float64 `json:"max_price"`
	AccommodationType  string  `json:"accommodation_type"`
	OrderBy            string  `json:"order_by"`
	DelaySeconds       int32   `json:"delay_seconds"`
}

type SearchResponse struct {
	Hotels          []models.Hotel `json:"hotels"`
	HasAvailability bool           `json:"has_availability"`
}

var repository *models.HotelRepository

func searchHotelsHandler(w http.ResponseWriter, r *http.Request) {
	var req SearchRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// Simulate processing delay
	if req.DelaySeconds > 0 {
		time.Sleep(time.Duration(req.DelaySeconds) * time.Second)
	}

	hotels := repository.SearchHotels(
		req.City,
		req.MinStars,
		req.MaxStars,
		req.MinPrice,
		req.MaxPrice,
		req.AccommodationType,
		req.OrderBy,
	)

	hasAvailability := false
	for _, hotel := range hotels {
		if hotel.Available {
			hasAvailability = true
			break
		}
	}

	response := SearchResponse{
		Hotels:          hotels,
		HasAvailability: hasAvailability,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "OK",
		"service": "Hoteis REST",
	})
}

func main() {
	repository = models.NewHotelRepository()

	r := mux.NewRouter()
	r.HandleFunc("/hotels/search", searchHotelsHandler).Methods("POST")
	r.HandleFunc("/health", healthHandler).Methods("GET")

	// CORS
	handler := cors.Default().Handler(r)

	log.Println("=" + "=" * 58)
	log.Println("Servidor REST de Hotéis rodando na porta 5002")
	log.Println("Para comparação de performance com gRPC")
	log.Println("=" + "=" * 58)

	if err := http.ListenAndServe(":5002", handler); err != nil {
		log.Fatal(err)
	}
}
