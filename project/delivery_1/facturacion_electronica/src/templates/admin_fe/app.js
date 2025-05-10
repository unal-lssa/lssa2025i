const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());
app.use(express.urlencoded({extended: true}));

// Puerto de escucha del Frontend
const ADMIN_FRONTEND_PORT = process.env.ADMIN_FRONTEND_PORT || 5002;

// Host del API Gateway
const API_GATEWAY_HOST = process.env.API_GATEWAY_HOST || 'efact_ag';
// Puerto de escucha del API Gateway
const API_GATEWAY_PORT = process.env.API_GATEWAY_PORT || 5000;

// URL del API Gateway
const API_GATEWAY_URL = `http://${API_GATEWAY_HOST}:${API_GATEWAY_PORT}`;

// Index
app.get('/', async (req, res) => {
    try {
        // Respuesta HTML
        res.send(`
            <html>
                <body>
                    <!-- Formulario para leer facturas -->
                    <h2>Leer facturas</h2>
                    <form action="/invoice" method="GET">
                        <!-- Dummy -->
                        <label for="name">ID Factura:</label>
                        <input type="text" id="name" name="name" required>
                        <button type="submit">Leer</button>
                    </form>
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send("Error contacting backend");
    }
});

// Endpoint para leer facturas
app.get('/invoice', async (req, res) => {
    // Dummy
    await axios.get(`${API_GATEWAY_URL}/invoice`);
    res.redirect('/');
});

// Endpoint para leer factura por id
app.get('/invoice/:id', async (req, res) => {
    // Dummy
    const { id } = req.params;
    try {
        // Llamada al API Gateway
        const response = await axios.get(`${API_GATEWAY_URL}/invoice/${id}`);
        // Respuesta HTML
        res.send(`
            <html>
                <body>
                    <h2>Factura ${id}</h2>
                    <pre>${JSON.stringify(response.data, null, 2)}</pre>
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send("Error contacting backend");
    }
});

// App listening
app.listen(ADMIN_FRONTEND_PORT, () => console.log(`Frontend Admin running on port ${ADMIN_FRONTEND_PORT}`));
