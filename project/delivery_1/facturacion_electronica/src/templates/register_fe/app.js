const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());
app.use(express.urlencoded({extended: true}));

// Puerto de escucha del Frontend
const REGISTER_FRONTEND_PORT = process.env.REGISTER_FRONTEND_PORT || 5001;

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
                    <!--DEBUG-->
                    
                    <!-- Formulario para crear un nuevo vendedor -->
                    <h2>Crear nuevo vendedor</h2>
                    <form action="/seller" method="POST">
                        <!-- Dummy -->
                        <label for="name">Nombre:</label>
                        <input type="text" id="name" name="name" required>
                        <button type="submit">Crear</button>
                    </form>
                    <!-- Formulario para crear un nuevo comprador -->
                    <h2>Crear nuevo comprador</h2>
                    <form action="/buyer" method="POST">
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

// Endpoint ping
app.get('/ping', async (req, res) => {
    try {
        const response = await axios.get(`${API_GATEWAY_URL}/ping`);
        res.send(
            {
                status: response.status,
                data: response.data,
                message: "Ping to API Gateway successful"
            }
        );
    } catch (err) {
        res.status(500).send("Error contacting API Gateway" + err);
    }
});

// Endpoint para crear un nuevo usuario con role seller
app.post('/seller', async (req, res) => {
    // Role seller
    const seller = req.body.seller;
    await axios.post(`${API_GATEWAY_URL}/user`, {seller});
    res.redirect('/');
});

// Endpoint para crear un nuevo usuario con role buyer
app.post('/buyer', async (req, res) => {
    // Role buyer
    const seller = req.body.seller;
    await axios.post(`${API_GATEWAY_URL}/user`, {seller});
    res.redirect('/');
});

// App listening
app.listen(REGISTER_FRONTEND_PORT, () => console.log(`Frontend Register running on port ${REGISTER_FRONTEND_PORT}`));
