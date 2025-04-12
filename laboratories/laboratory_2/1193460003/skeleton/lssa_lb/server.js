
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

app.use('/', createProxyMiddleware({
    target: 'http://lssa_be:80',
    changeOrigin: true
}));

app.listen(80, () => {
    console.log('load_balancer running on port 80');
});
