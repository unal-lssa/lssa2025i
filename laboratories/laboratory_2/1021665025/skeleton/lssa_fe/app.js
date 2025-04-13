
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const BACKEND_URL = 'http://lssa_ldb:80';

app.get('/', async (req, res) => {
try {
    const response = await axios.get(`${BACKEND_URL}/systems`);
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
    res.status(500).send("Error contacting backend");
}
});

app.post('/create', async (req, res) => {
const name = req.body.name;
await axios.post(`${BACKEND_URL}/create`, { name });
res.redirect('/');
});

app.listen(80, () => console.log("Frontend running on port 80"));
