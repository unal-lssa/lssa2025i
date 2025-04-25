const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());
app.use(express.urlencoded({extended: true}));

// Puerto de escucha del Frontend
const SELLER_FRONTEND_PORT = process.env.SELLER_FRONTEND_PORT || 5002;

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
                    <!-- Formulario para registrar una factura -->
                    <h2>Registrar nueva factura</h2>
                    <form action="/invoice" method="POST">
                        <!-- Dummy -->
                        <label for="name">Nombre:</label>
                        <input type="text" id="name" name="name" required>
                        <button type="submit">Crear</button>
                    </form>
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send("Error contacting backend");
    }
});

// Endpoint para crear un nuevo usuario con role seller
app.post('/invoice', async (req, res) => {
    // Invoice data
    const invoice = req.body.invoice;
    await axios.post(`${API_GATEWAY_URL}/invoice`, {invoice});
    res.redirect('/');
});

// App listening
app.listen(SELLER_FRONTEND_PORT, () => console.log(`Frontend Seller running on port ${SELLER_FRONTEND_PORT}`));
