package middlewares

import (
	"errors"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte(os.Getenv("JWT_SECRET"))

func TokenRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := c.Request.Header.Get("Authorization")
		if token == "" {
			c.AbortWithStatusJSON(
				http.StatusUnauthorized,
				gin.H{"message": "No token provided in Authorization header"},
			)
			return
		}

		if splits := strings.Split(token, " "); len(splits) == 2 {
			token = splits[1]
		}

		if _, err := validateJWT(token); err != nil {
			c.AbortWithStatusJSON(
				http.StatusUnauthorized,
				gin.H{"message": "Error validating token", "error": err.Error()},
			)
			return
		}

		c.Next()
	}
}

func validateJWT(tokenString string) (jwt.MapClaims, error) {
	token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
		// Validamos que el método de firma sea HMAC
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("Invalid sign")
		}
		return jwtSecret, nil
	})

	if err != nil || !token.Valid {
		return nil, errors.New("Invalid token")
	}

	// Convertimos a MapClaims para poder acceder a los datos
	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, errors.New("Error reading claims")
	}

	return claims, nil
}
