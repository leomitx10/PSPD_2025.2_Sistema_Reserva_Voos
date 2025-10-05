.PHONY: proto build run clean client

proto:
	protoc --go_out=. --go_opt=paths=source_relative \
		--go-grpc_out=. --go-grpc_opt=paths=source_relative \
		proto/hotel.proto

build:
	go build -o bin/hotel-server cmd/server/main.go

build-client:
	go build -o bin/hotel-client cmd/client/main.go

run:
	go run cmd/server/main.go

client:
	go run cmd/client/main.go

clean:
	rm -rf bin/

deps:
	go mod tidy
	go mod download

test:
	go test ./...
