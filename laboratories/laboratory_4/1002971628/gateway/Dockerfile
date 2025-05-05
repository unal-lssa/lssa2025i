FROM golang:1.24.2 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o api_gateway .

FROM gcr.io/distroless/base-debian12

WORKDIR /

COPY --from=builder /app/api_gateway .

ENTRYPOINT ["/api_gateway"]
