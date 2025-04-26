
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const API_GATEWAY_URL = 'http://lssa_api_gw:80';

app.get('/', (req, res) => {
    res.send(`
    <html>
        <body>
            <h1>Login Page</h1>
            <form method="POST" action="/login">
                <div>
                    <label for="username">Username:</label>
                    <input id="username" name="username" required />
                </div>
                <div style="margin-top: 10px;">
                    <label for="password">Password:</label>
                    <input id="password" name="password" type="password" required />
                </div>
                <div style="margin-top: 10px;">
                    <button type="submit">Login</button>
                </div>
            </form>
            <p style="color: gray; margin-top: 20px;">
                Default credentials: user1 / password123
            </p>
        </body>
    </html>
    `);
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    try {
        const response = await axios.post(`${API_GATEWAY_URL}/login`, { username, password });
        const token = response.data.token;

        // Redirect to main frontend with token
        res.redirect(`http://localhost:8002/?token=${token}`);
    } catch (err) {
        console.error("Login error:", err.message);
        res.status(401).send(`
            <html>
                <body>
                    <h2>Invalid credentials</h2>
                    <p>Please try again</p>
                    <a href="/">Back to login</a>
                </body>
            </html>
        `);
    }
});

app.listen(80, () => console.log("Login Frontend running on port 80"));
