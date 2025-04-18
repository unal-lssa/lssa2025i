package main

import (
	"ddaniel27/gateway/handlers"
	"ddaniel27/gateway/middlewares"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	limiter := middlewares.NewRateLimiter(5, 8)

	r.Use(middlewares.Whitelisting())
	r.Use(middlewares.Ratelimit(limiter))

	r.POST("/login", handlers.PostLogin)
	r.GET("/data", middlewares.TokenRequired(), handlers.GetData)

	r.Run(":8080")
}
