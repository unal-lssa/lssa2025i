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
                    <!-- Formulario para crear un nuevo usuario -->
                    <h2>Crear nuevo usuario</h2>
                    <form action="/user" method="POST">
                        <label for="name">Nombre:</label>
                        <input type="text" id="name" name="name" required>
                        <label for="role_name">Rol:</label>
                        <input type="text" id="role_name" name="role_name" required>
                        <label for="doc_id">ID Documento:</label>
                        <input type="text" id="doc_id" name="doc_id" required>
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
app.post('/user', async (req, res) => {
    const { name, role_name, doc_id } = req.body;
    await axios.post(`${API_GATEWAY_URL}/users`, { name, role_name, doc_id });
    res.redirect('/');
});

// App listening
app.listen(REGISTER_FRONTEND_PORT, () => console.log(`Frontend Register running on port ${REGISTER_FRONTEND_PORT}`));
