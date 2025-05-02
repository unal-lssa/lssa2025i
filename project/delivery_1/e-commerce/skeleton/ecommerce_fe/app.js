
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const API_GATEWAY_URL = 'http://ecommerce_ag_us:80';

app.get('/', async (req, res) => {
try {
    const response = await axios.get(`${API_GATEWAY_URL}/systems`);
    const systems = response.data.systems;
    let list = systems.map(([id, name]) => `<li>${name}</li>`).join('');
    res.send(`
    <html>
        <body>
        <h1>Frontend</h1>
        <form method="POST" action="/create">
            <input name="name" />
            <button type="submit">Create</button>
        </form>
        <ul>${list}</ul>
        </body>
    </html>
    `);
} catch (err) {
    console.error("Error connecting to API Gateway:", err.message);
    res.status(500).send("Error contacting API Gateway");
}
});

app.post('/create', async (req, res) => {
try {
    const name = req.body.name;
    await axios.post(`${API_GATEWAY_URL}/create`, { name });
    res.redirect('/');
} catch (err) {
    console.error("Error sending data to API Gateway:", err.message);
    res.status(500).send("Error processing your request");
}
});

app.get('/health', async (req, res) => {
    res.status(200).send("Healthcheck OK!");
});

app.listen(80, () => console.log("Frontend running on port 80"));
