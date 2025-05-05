package middlewares

import (
	"ddaniel27/gateway/cache"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"slices"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

const REDIS_KEY string = "ValidIPs"

var WHITELIST_HOST string = os.Getenv("WHITELIST_HOST")

type whitelist struct {
	IP string `json:"ip"`
}

func Whitelisting(cs *cache.Cache) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		val, err := cs.GetStringSliceFromCache(ctx, REDIS_KEY)

		if err == redis.Nil {
			res, err := getWhitelist()
			if err != nil {
				c.AbortWithStatusJSON(
					http.StatusInternalServerError,
					gin.H{"error": err.Error(), "message": "error getting whitelists"},
				)
				return
			}

			whitelists := []string{}
			for _, wl := range res {
				whitelists = append(whitelists, wl.IP)
			}

			if err = cs.SetInCache(ctx, REDIS_KEY, whitelists); err != nil {
				c.AbortWithStatusJSON(
					http.StatusInternalServerError,
					gin.H{"error": err.Error(), "message": "error setting whitelists"},
				)
				return
			}

			val = whitelists
		} else if err != nil {
			c.AbortWithStatusJSON(
				http.StatusInternalServerError,
				gin.H{"error": err.Error()},
			)
			return
		}

		if !slices.Contains(val, c.ClientIP()) {
			c.AbortWithStatusJSON(
				http.StatusForbidden,
				gin.H{"message": "not in whitelist", "IP": c.ClientIP()},
			)
			return
		}

		c.Next()
	}
}

func getWhitelist() ([]whitelist, error) {
	resp, err := http.Get(fmt.Sprintf("http://%s:8082/whitelist", WHITELIST_HOST))
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
