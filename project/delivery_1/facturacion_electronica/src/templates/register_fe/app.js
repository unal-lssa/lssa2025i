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
                <form action="/register?token=${token}" method="POST">
                    <label>Tipo de registro:</label><br>
                    <input type="radio" id="comprador" name="role_name" value="Comprador" onclick="toggleLegalName()" required>
                    <label for="comprador">Comprador</label><br>
                    <input type="radio" id="vendedor" name="role_name" value="Vendedor" onclick="toggleLegalName()" required>
                    <label for="vendedor">Vendedor</label><br><br>

                    <label>Tipo de documento:</label><br>
                    <input type="radio" id="cc" name="doc_type" value="C.C" required>
                    <label for="cc">C.C</label><br>
                    <input type="radio" id="nit" name="doc_type" value="NIT" required>
                    <label for="nit">NIT</label><br><br>

                    <label for="doc_id">Número de documento:</label><br>
                    <input type="text" id="doc_id" name="doc_id" required><br><br>

                    <label for="first_name">Nombres:</label><br>
                    <input type="text" id="first_name" name="first_name" required><br><br>

                    <label for="last_name">Apellidos:</label><br>
                    <input type="text" id="last_name" name="last_name" required><br><br>

                    <div id="legal_name_field" style="display: none;">
                        <label for="legal_name">Razón Social:</label><br>
                        <input type="text" id="legal_name" name="legal_name"><br><br>
                    </div>

                    <button type="submit">Registrar</button>
                </form>

                <button type="button" onclick="window.location.href='/list-users?token=${token}'">
                    Ir a Listar Usuarios
                </button>

                <script>
                function toggleLegalName() {
                    const vendedorSelected = document.getElementById('vendedor').checked;
                    const legalNameField = document.getElementById('legal_name_field');
                    legalNameField.style.display = vendedorSelected ? 'block' : 'none';
                }
                </script>
            </html>
        `);
    } catch (err) {
        res.status(500).send("Error contacting backend" + err);
    }
});

// Endpoint para el registro
app.post('/register', async (req, res) => {
    try {
        const { doc_type, doc_id, first_name, last_name, role_name, legal_name } = req.body;

        // Obtener el token de la query string
        const token = req.query.token;
        console.log("Token: ", token);

        // Llamada al API Gateway para registrar al usuario con el token
        // Se agrega el token a la cabecera de la peticion
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.post(`${API_GATEWAY_URL}/register`, { doc_type, doc_id, first_name, last_name, role_name, legal_name }, { headers });
        console.log("Response: ", response.data);

        // Si el registro es exitoso, redirigir a la pagina de inicio
        if (response.status === 201) {
            res.redirect('/home?token=' + token);
        } else {
            res.status(500).send("Error registering user");
        }
    } catch (err) {
        res.status(500).send("Error contacting backend" + err);
    }
});


// Endpoint para listar los usuarios
app.get('/list-users', async (req, res) => {
    try {
        // Obtener el token de la query string
        const token = req.query.token;
        console.log("Token: ", token);

        // Llamada al API Gateway para listar los usuarios con el token
        // Se agrega el token a la cabecera de la peticion
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get(`${API_GATEWAY_URL}/list-users`, { headers });
        console.log("Response: ", response.data);

        // Si la lista de usuarios es exitosa, mostrar la lista
        if (response.status === 200) {
            res.send(`
                <html>
                    <body>
                        <h1>Lista de Usuarios</h1>
                        <ul>
                            ${response.data.map(user => `<li>${user.role_name} ${user.first_name} ${user.last_name} ${user.doc_type} ${user.doc_id} ${user.legal_name}</li>`).join('')}
                        </ul>
                    </body>
                </html>
            `);
        } else {
            res.status(500).send("Error listing users");
        }
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
