package handlers

import (
	"ddaniel27/microservice/db"
	"ddaniel27/microservice/models"
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetBooks(c *gin.Context) {
	var books []models.Book
	db.DB.Find(&books)
	c.JSON(http.StatusOK, books)
}
