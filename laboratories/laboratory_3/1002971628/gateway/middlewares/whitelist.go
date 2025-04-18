package middlewares

import (
	"encoding/json"
	"fmt"
	"net/http"
	"slices"

	"github.com/gin-gonic/gin"
)

type whitelist struct {
	IP string `json:"ip"`
}

var whitelists []string = []string{}

func Whitelisting() gin.HandlerFunc {
	return func(c *gin.Context) {
		if len(whitelists) == 0 {
			res, err := getWhitelist()
			if err != nil {
				c.AbortWithStatusJSON(
					http.StatusInternalServerError,
					gin.H{"error": err.Error(), "message": "error getting whitelists"},
				)
				return
			}

			for _, wl := range res {
				whitelists = append(whitelists, wl.IP)
			}
		}

		if !slices.Contains(whitelists, c.RemoteIP()) {
			c.AbortWithStatusJSON(
				http.StatusForbidden,
				gin.H{"message": "not in whitelist", "IP": c.RemoteIP()},
			)
			return
		}

		c.Next()
	}
}

func getWhitelist() ([]whitelist, error) {
	resp, err := http.Get("http://whitelist:8082/whitelist")
	if err != nil {
		return nil, fmt.Errorf("error calling to whitelist: %w", err)
	}
	defer resp.Body.Close()

	var data []whitelist
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return nil, fmt.Errorf("error decoding JSON: %w", err)
	}

	return data, nil
}
