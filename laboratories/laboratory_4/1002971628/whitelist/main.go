package main

import (
	"ddaniel27/whitelist/db"
	"ddaniel27/whitelist/handlers"

	"github.com/gin-gonic/gin"
)

func main() {
	db.Init()

	r := gin.Default()

	r.GET("/whitelist", handlers.GetWhitelists)

	r.Run(":8082")
}
