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
        // Fetch users from the API Gateway
        const response = await axios.get(`${API_GATEWAY_URL}/users`);
        const users = response.data.users;

        // Generate HTML to display the list of users
        let usersList = '<ul>';
        users.forEach(user => {
            usersList += `<li>Nombre: ${user.name}, Rol: ${user.role_name}, ID Documento: ${user.doc_id}</li>`;
        });
        usersList += '</ul>';

        // Send the response with the list of users
        res.send(`
            <html>
                <body>
                    <h2>Lista de Usuarios</h2>
                    ${usersList}
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send("Error contacting backend");
    }
});

// App listening
app.listen(ADMIN_FRONTEND_PORT, () => console.log(`Frontend Admin running on port ${ADMIN_FRONTEND_PORT}`));
