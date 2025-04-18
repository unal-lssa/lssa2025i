package handlers

import (
	"ddaniel27/whitelist/db"
	"ddaniel27/whitelist/models"
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetWhitelists(c *gin.Context) {
	var whitelists []models.Whitelist
	db.DB.Find(&whitelists)
	c.JSON(http.StatusOK, whitelists)
}
