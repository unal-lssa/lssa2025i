package cache

import (
	"context"
	"log"

	"github.com/go-redis/redis/v8"
)

type Cache struct {
	rdb *redis.Client
}

func Init() *Cache {
	rdb := redis.NewClient(&redis.Options{
		Addr:     "cache:6379",
		Password: "",
		DB:       0,
	})

	ctx := context.Background()
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Error al conectar a Redis: %v", err)
	}

	return &Cache{rdb: rdb}
}
