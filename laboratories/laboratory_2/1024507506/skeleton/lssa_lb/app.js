
const express = require('express');
const httpProxy = require('http-proxy');
const app = express();
const proxy = httpProxy.createProxyServer({});
const targets = ['lssa_be1', 'lssa_be2'].map(host => `http://${host}:80`);
let index = 0;

app.use((req, res) => {
    const target = targets[index % targets.length];
    index++;
    proxy.web(req, res, { target });
});

app.listen(80, () => console.log("Load balancer running on port 80"));
