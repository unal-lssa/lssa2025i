package handlers

import (
	"io"
	"net/http"
	"net/url"
	"sync/atomic"

	"github.com/gin-gonic/gin"
)

var (
	apiGateways = []string{
		"http://gateway_1:8080",
		"http://gateway_2:8080",
	}
	counter uint32
)

func getNextGateway() string {
	index := atomic.AddUint32(&counter, 1)
	return apiGateways[(index-1)%uint32(len(apiGateways))]
}

func ForwardHandler(c *gin.Context) {
	target := getNextGateway()

	targetURL, err := url.JoinPath(target, c.Request.URL.Path)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error construyendo URL: %v", err)
		return
	}
	if c.Request.URL.RawQuery != "" {
		targetURL += "?" + c.Request.URL.RawQuery
	}

	req, err := http.NewRequest(c.Request.Method, targetURL, c.Request.Body)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error creando request: %v", err)
		return
	}
	req.Header = c.Request.Header.Clone()

	clientIP := c.ClientIP()
	if prior := req.Header.Get("X-Forwarded-For"); prior != "" {
		req.Header.Set("X-Forwarded-For", prior+", "+clientIP)
	} else {
		req.Header.Set("X-Forwarded-For", clientIP)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.String(http.StatusBadGateway, "Error enviando request: %v", err)
		return
	}
	defer resp.Body.Close()

	for k, v := range resp.Header {
		for _, val := range v {
			c.Writer.Header().Add(k, val)
		}
	}
	c.Writer.Header().Add("X-Gateway-Used", target)
	c.Writer.WriteHeader(resp.StatusCode)

	_, err = io.Copy(c.Writer, resp.Body)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error copiando body: %v", err)
	}
}
