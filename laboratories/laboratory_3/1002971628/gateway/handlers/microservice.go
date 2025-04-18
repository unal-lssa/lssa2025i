package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

type book struct {
	Title  string `json:"title"`
	Author string `json:"author"`
}

func GetData(c *gin.Context) {
	res, err := getBooks()
	if err != nil {
		c.JSON(
			http.StatusInternalServerError,
			gin.H{"error": err.Error(), "message": "error calling data"},
		)
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": res})
}

func getBooks() ([]book, error) {
	resp, err := http.Get("http://microservice:8081/microservice")
	if err != nil {
		return nil, fmt.Errorf("error calling microservice: %w", err)
	}
	defer resp.Body.Close()

	var data []book
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return nil, fmt.Errorf("error decoding JSON: %w", err)
	}

	return data, nil
}
