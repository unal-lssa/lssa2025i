
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const API_GATEWAY_URL = 'http://lssa_api_gw:80';

app.get('/', async (req, res) => {
    // Check if token exists in session
    const token = req.query.token;
    if (!token) {
        return res.redirect('/login-page');
    }

    try {
        const response = await axios.get(`${API_GATEWAY_URL}/data`, {
            headers: {
                'Authorization': token
            }
        });

        const systems = response.data.systems;
        let list = systems.map(([id, name]) => `<li>${name}</li>`).join('');

        res.send(`
        <html>
            <body>
                <h1>Frontend</h1>
                <form method="POST" action="/create">
                    <input name="name" />
                    <input type="hidden" name="token" value="${token}" />
                    <button type="submit">Create</button>
                </form>
                <ul>${list}</ul>
            </body>
        </html>
        `);
    } catch (err) {
        console.error("Error:", err.message);
        res.status(500).send("Error contacting API Gateway or unauthorized. <a href='/login-page'>Login again</a>");
    }
});

app.get('/login-page', (req, res) => {
    res.send(`
    <html>
        <body>
            <h2>Please login first</h2>
            <p>You need to login to access the system</p>
            <p>Redirect to <a href="http://localhost:8003">login page</a></p>
        </body>
    </html>
    `);
});

app.post('/create', async (req, res) => {
    const name = req.body.name;
    const token = req.body.token;

    try {
        await axios.post(`${API_GATEWAY_URL}/create`, { name }, {
            headers: {
                'Authorization': token
            }
        });
        res.redirect(`/?token=${token}`);
    } catch (err) {
        console.error("Error:", err.message);
        res.status(500).send("Error creating item or unauthorized. <a href='/login-page'>Login again</a>");
    }
});

app.listen(80, () => console.log("Frontend running on port 80"));
