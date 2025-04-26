
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

const BACKEND = 'http://lssa_be:80';

app.use('/', createProxyMiddleware({
    target: BACKEND,
    changeOrigin: true
}));

app.listen(80, () => {
    console.log('Load Balancer running on port 80');
});
