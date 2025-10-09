package models

import (
	"math/rand"
	"sort"
	"strings"
	"time"
)

type Hotel struct {
	ID                string
	Name              string
	City              string
	Stars             int32
	BasePrice         float64
	Available         bool
	Amenities         []string
	AccommodationType string
}

type HotelRepository struct {
	hotels []Hotel
}

func NewHotelRepository() *HotelRepository {
	return &HotelRepository{
		hotels: generateHotels(),
	}
}

func (hr *HotelRepository) SearchHotels(city string, minStars, maxStars int32, minPrice, maxPrice float64, accommodationType, orderBy string) []Hotel {
	var filtered []Hotel
	
	for _, hotel := range hr.hotels {
		currentPrice := hr.calculateDynamicPrice(hotel.BasePrice)
		hotel.BasePrice = currentPrice
		
		if !hr.matchesFilters(hotel, city, minStars, maxStars, minPrice, maxPrice, accommodationType) {
			continue
		}
		
		hotel.Available = rand.Float32() < 0.9
		
		filtered = append(filtered, hotel)
	}
	
	hr.sortHotels(filtered, orderBy)
	
	return filtered
}

func (hr *HotelRepository) matchesFilters(hotel Hotel, city string, minStars, maxStars int32, minPrice, maxPrice float64, accommodationType string) bool {
	if city != "" && !strings.EqualFold(hotel.City, city) {
		return false
	}

	if minStars > 0 && hotel.Stars < minStars {
		return false
	}

	if maxStars > 0 && hotel.Stars > maxStars {
		return false
	}

	if minPrice > 0 && hotel.BasePrice < minPrice {
		return false
	}

	if maxPrice > 0 && hotel.BasePrice > maxPrice {
		return false
	}

	if accommodationType != "" && !strings.EqualFold(hotel.AccommodationType, accommodationType) {
		return false
	}

	return true
}

func (hr *HotelRepository) calculateDynamicPrice(basePrice float64) float64 {
	variation := (rand.Float64() - 0.5) * 0.6
	return basePrice * (1 + variation)
}

func (hr *HotelRepository) sortHotels(hotels []Hotel, orderBy string) {
	switch orderBy {
	case "price":
		sort.Slice(hotels, func(i, j int) bool {
			return hotels[i].BasePrice < hotels[j].BasePrice
		})
	case "rating":
		sort.Slice(hotels, func(i, j int) bool {
			return hotels[i].Stars > hotels[j].Stars
		})
	}
}

func generateHotels() []Hotel {
	cities := []string{"São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Belo Horizonte", "Recife", "Manaus", "Porto Alegre"}
	accommodationTypes := []string{"Hotel", "Pousada", "Resort", "Hostel"}
	amenities := []string{"Wi-Fi", "Piscina", "Academia", "Spa", "Restaurante", "Estacionamento", "Café da Manhã", "Ar Condicionado"}

	var hotels []Hotel

	for _, city := range cities {
		numHotels := rand.Intn(21) + 30 
		for i := 0; i < numHotels; i++ {
			accType := accommodationTypes[rand.Intn(len(accommodationTypes))]
			stars := int32(rand.Intn(5) + 1)

			basePrice := float64(int(stars)*80 + rand.Intn(300))
			if accType == "Resort" {
				basePrice *= 1.8
			} else if accType == "Hostel" {
				basePrice *= 0.35
			} else if accType == "Pousada" {
				basePrice *= 0.7
			}

			selectedAmenities := make([]string, 0)
			for _, amenity := range amenities {
				if rand.Float32() < 0.65 {
					selectedAmenities = append(selectedAmenities, amenity)
				}
			}

			hotels = append(hotels, Hotel{
				ID:                generateID(),
				Name:              generateHotelName(city, accType),
				City:              city,
				Stars:             stars,
				BasePrice:         basePrice,
				Available:         true, 
				Amenities:         selectedAmenities,
				AccommodationType: accType,
			})
		}
	}

	for len(hotels) < 1000 {
		city := cities[rand.Intn(len(cities))]
		accType := accommodationTypes[rand.Intn(len(accommodationTypes))]
		stars := int32(rand.Intn(5) + 1)

		basePrice := float64(int(stars)*80 + rand.Intn(300))
		if accType == "Resort" {
			basePrice *= 1.8
		} else if accType == "Hostel" {
			basePrice *= 0.35
		} else if accType == "Pousada" {
			basePrice *= 0.7
		}

		selectedAmenities := make([]string, 0)
		for _, amenity := range amenities {
			if rand.Float32() < 0.65 {
				selectedAmenities = append(selectedAmenities, amenity)
			}
		}

		available := rand.Float32() < 0.85

		hotels = append(hotels, Hotel{
			ID:                generateID(),
			Name:              generateHotelName(city, accType),
			City:              city,
			Stars:             stars,
			BasePrice:         basePrice,
			Available:         available,
			Amenities:         selectedAmenities,
			AccommodationType: accType,
		})
	}

	return hotels
}

func generateID() string {
	return time.Now().Format("20060102150405") + string(rune(rand.Intn(1000)))
}

func generateHotelName(city, accType string) string {
	prefixes := []string{"Grand", "Royal", "Palace", "Central", "Premium"}
	suffixes := []string{"Plaza", "Inn", "Suites", "Park", "Tower"}
	
	prefix := prefixes[rand.Intn(len(prefixes))]
	suffix := suffixes[rand.Intn(len(suffixes))]
	
	return prefix + " " + city + " " + suffix
}
