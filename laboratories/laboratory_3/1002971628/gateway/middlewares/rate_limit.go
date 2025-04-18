package middlewares

import (
	"net/http"
	"sync"

	"github.com/gin-gonic/gin"
	"golang.org/x/time/rate"
)

type RateLimiter struct {
	ips   map[string]*rate.Limiter
	mu    sync.Mutex
	r     rate.Limit
	burst int
}

func NewRateLimiter(r rate.Limit, burst int) *RateLimiter {
	return &RateLimiter{
		ips:   make(map[string]*rate.Limiter),
		r:     r,
		burst: burst,
	}
}

func (rl *RateLimiter) GetLimiter(ip string) *rate.Limiter {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	limiter, exists := rl.ips[ip]
	if !exists {
		limiter = rate.NewLimiter(rl.r, rl.burst)
		rl.ips[ip] = limiter
	}

	return limiter
}

func Ratelimit(rl *RateLimiter) gin.HandlerFunc {
	return func(c *gin.Context) {
		limiter := rl.GetLimiter(c.ClientIP())

		if !limiter.Allow() {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{"error": "Too many request"})
			return
		}

		c.Next()
	}
}
