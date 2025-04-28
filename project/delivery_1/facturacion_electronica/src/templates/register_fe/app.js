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
app.get('/login', async (req, res) => {
    try {
        // Respuesta HTML
        res.send(`
            <html>
                <body>
                    <!--LOGIN-->
                    <form action="/login" method="POST">
                        <label for="doc_id">Doc ID:</label><br>
                        <input type="text" id="doc_id" name="doc_id" required><br><br>
                        <label for="password">Password:</label><br>
                        <input type="password" id="password" name="password" required><br><br>
                        <button type="submit">Login</button>
                    </form>
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send("Error contacting backend");
    }
});

// Endpoint para el login
app.post('/login', async (req, res) => {
    try {
        const { doc_id, password } = req.body;
        console.log("doc_id: ", doc_id);
        console.log("password: ", password);

        // Llamada al API Gateway para autenticar al usuario
        const response = await axios.post(`${API_GATEWAY_URL}/login`, { doc_id, password });
        console.log("Response: ", response.data);

        // Si la autenticacion es exitosa, redirigir a la pagina de inicio con el token
        if (response.status === 200) {
            res.redirect('/home?token=' + response.data.token);
        } else if (response.status === 401) {
            res.status(401).send("Invalid credentials");
        }
        else {
            res.status(500).send("Error authenticating user");
        }
    } catch (err) {
        res.status(500).send("Error contacting backend" + err);
    }
});

// Endpoint para la pagina de inicio
app.get('/home', async (req, res) => {
    try {
        const token = req.query.token;

        // Respuesta HTML
        res.send(`
            <html>
                <body>
                    <p>Your token is ${token}</p>
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send("Error contacting backend" + err);
    }
});

// Endpoint ping para verificar la comunicacion con el API Gateway
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

// Endpoint ping para verificar la comunicacion con el Microservicio de Users
app.get('/ping-users', async (req, res) => {
    try {
        const response = await axios.get(`${API_GATEWAY_URL}/ping-users`);
        res.send(
            {
                status: response.status,
                data: response.data,
                message: "Ping to User Microservice successful"
            }
        );
    } catch (err) {
        res.status(500).send("Error contacting User Microservice" + err);
    }
});


// App listening
app.listen(REGISTER_FRONTEND_PORT, () => console.log(`Frontend Register running on port ${REGISTER_FRONTEND_PORT}`));
