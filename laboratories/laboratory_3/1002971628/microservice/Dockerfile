FROM golang:1.24.2 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o microservice .

FROM gcr.io/distroless/base-debian12

WORKDIR /

COPY --from=builder /app/microservice .

ENTRYPOINT ["/microservice"]
