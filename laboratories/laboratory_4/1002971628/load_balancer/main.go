package main

import (
	"ddaniel27/load_balancer/handlers"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.Any("/*path", handlers.ForwardHandler)

	r.Run(":8080")
}
