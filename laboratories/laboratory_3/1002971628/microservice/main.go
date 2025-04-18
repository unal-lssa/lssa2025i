package main

import (
	"ddaniel27/microservice/db"
	"ddaniel27/microservice/handlers"

	"github.com/gin-gonic/gin"
)

func main() {
	db.Init()

	r := gin.Default()

	r.GET("/microservice", handlers.GetBooks)

	r.Run(":8081")
}
