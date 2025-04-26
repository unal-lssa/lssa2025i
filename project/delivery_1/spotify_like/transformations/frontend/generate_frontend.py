import os, textwrap

def generate_frontend(name, backend=None, connections=None):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    # Default simple app
    app_code = textwrap.dedent("""
        const express = require('express');
        const app = express();

        app.get('/', (req, res) => {
            res.send('<h1>Hello World from Frontend</h1>');
        });

        app.listen(80, () => console.log("Frontend running on port 80"));
    """)

    # Only add connection code if this is a "from" component in a connector
    if connections:
        for conn_type, target in connections.items():
            if conn_type == "http" and target:
                app_code = textwrap.dedent(f"""
                    const express = require('express');
                    const axios = require('axios');
                    const app = express();
                    
                    const BACKEND_URL = 'http://{target}:80';

                    app.get('/', async (req, res) => {{
                        try {{
                            const response = await axios.get(BACKEND_URL);
                            res.send(`
                                <h1>Hello World from Frontend</h1>
                                <p>Backend response: ${{JSON.stringify(response.data)}}</p>
                            `);
                        }} catch (err) {{
                            res.send(`
                                <h1>Hello World from Frontend</h1>
                                <p>Error connecting to backend: ${{err.message}}</p>
                            `);
                        }}
                    }});

                    app.listen(80, () => console.log("Frontend running on port 80"));
                """)

    with open(os.path.join(path, 'package.json'), 'w') as f:
        f.write(textwrap.dedent("""
            {
                "name": "frontend",
                "version": "1.0.0",
                "main": "app.js",
                "dependencies": {
                    "express": "^4.18.2",
                    "axios": "^1.6.7"
                }
            }
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM node:18
                                
            WORKDIR /app
            COPY . .
            RUN npm install
                                
            CMD ["node", "app.js"]
            """
        ))

    with open(os.path.join(path, 'app.js'), 'w') as f:
        f.write(app_code)