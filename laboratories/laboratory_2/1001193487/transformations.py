import os, textwrap

def generate_database(name):

    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'init.sql'), 'w') as f:
        f.write(textwrap.dedent("""
            CREATE TABLE IF NOT EXISTS systems (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255)
            );
            """
        ))

def generate_backend(name, database):
	path = f'skeleton/{name}'
	os.makedirs(path, exist_ok=True)
	with open(os.path.join(path, 'app.py'), 'w') as f:
		f.write(textwrap.dedent(f"""
			from flask import Flask, request, jsonify
			import mysql.connector
			app = Flask(__name__)
			@app.route('/create', methods=['POST'])
			def create():
				data = request.json
				conn = mysql.connector.connect(
				host='{database}',
				user='root',
				password='root',
				database='{database}'
				)
				cursor = conn.cursor()
				cursor.execute("INSERT INTO systems (name) VALUES (%s)", (data['name'],))
				conn.commit()
				cursor.close()
				conn.close()
				return jsonify(status="created")
			@app.route('/systems')
			def get_systems():
				conn = mysql.connector.connect(
					host='{database}',
					user='root',
					password='root',
					database='{database}'
				)
				cursor = conn.cursor()
				cursor.execute("SELECT * FROM systems")
				rows = cursor.fetchall()
				cursor.close()
				conn.close()
				return jsonify(systems=rows)
			if __name__ == '__main__':
				app.run(host='0.0.0.0', port=80)
		"""
		))
	with open(os.path.join(path, 'Dockerfile'), 'w') as f:
		f.write(textwrap.dedent("""
			FROM python:3.11-slim
			WORKDIR /app
			COPY . .
			RUN pip install flask mysql-connector-python
			CMD ["python", "app.py"]
		"""
		))

def generate_load_balancer(name, backend: str, instances: int = 1):
	path = f'skeleton/{name}'
	os.makedirs(path, exist_ok=True)
	backslash_char = '\n'
	with open(os.path.join(path, 'nginx.conf'), 'w') as f:
		f.write(textwrap.dedent(f"""
			worker_processes 1;
			events {{
				worker_connections 1024;
			}}
			http {{
				upstream backend_servers {{
					least_conn;
					{f"{backslash_char}	".join([f'server {backend}_{i}:80;' for i in range(1, instances + 1)])}
				}}
				server {{
					listen 80;
					location / {{
						proxy_pass http://backend_servers;
					}}
				}}
			}}
		"""
		))
	with open(os.path.join(path, 'Dockerfile'), 'w') as f:
		f.write(textwrap.dedent("""
			FROM nginx:latest
			COPY nginx.conf /etc/nginx/nginx.conf
		"""
		))


def generate_frontend(name, backend):
	path = f'skeleton/{name}'
	os.makedirs(path, exist_ok=True)
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
		f.write(textwrap.dedent(f"""
			const express = require('express');
			const axios = require('axios');
			const app = express();
			app.use(express.json());
			app.use(express.urlencoded({{ extended: true }}));
			const BACKEND_URL = 'http://{backend}:80';
			app.get('/', async (req, res) => {{
			try {{
			const response = await
			axios.get(`${{BACKEND_URL}}/systems`);
			const systems = response.data.systems;
			let list = systems.map(([id, name]) => `<li>${{name}}
			</li>`).join('');
			res.send(`
			<html>
			<body>
			<h1>Frontend</h1>
			<form method="POST" action="/create">
			<input name="name" />
			<button type="submit">Create</button>
			</form>
			<ul>${{list}}</ul>
			</body>
			</html>
			`);
			}} catch (err) {{
			res.status(500).send("Error contacting backend");
			}}
			}});
			app.post('/create', async (req, res) => {{
			const name = req.body.name;
			await axios.post(`${{BACKEND_URL}}/create`, {{ name }});
			res.redirect('/');
			}});
			app.listen(80, () => console.log("Frontend running on port 80"));
		"""
		))
def generate_docker_compose(components, backend_name, backend_instances=1):
	path = f'skeleton/'
	os.makedirs(path, exist_ok=True)
	with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
		sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else 1))
		f.write("services:\n")
		db = None
		for i, (name, ctype) in enumerate(sorted_components.items()):
			port = 8000 + i
			if ctype == "database":
				db = name
				f.write(f"  {name}:\n")
				f.write("    image: mysql:8\n")
				f.write("    environment:\n")
				f.write("      - MYSQL_ROOT_PASSWORD=root\n")
				f.write(f"      - MYSQL_DATABASE={name}\n")
				f.write("    volumes:\n")
				f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
				f.write("    ports:\n")
				f.write("      - '3307:3306'\n")
			elif ctype == "backend":
				for j in range(1, backend_instances + 1):
					f.write(f"  {name}_{j}:\n")
					f.write(f"    build: ./{name}\n")
					f.write("    depends_on:\n")
					f.write(f"      - {db}\n")
			elif ctype == "load_balancer":
				f.write(f"  {name}:\n")
				f.write(f"    build: ./{name}\n")
				f.write("    ports:\n")
				f.write("      - '80:80'\n")
				f.write("    depends_on:\n")
				f.write(f"      - {db}\n")
				for j in range(1, backend_instances + 1):
					f.write(f"      - {backend_name}_{j}\n")
			else:
				f.write(f"  {name}:\n")
				f.write(f"    build: ./{name}\n")
				f.write("    ports:\n")
				f.write(f"      - '{port}:80'\n")
		f.write("\nnetworks:\n  default:\n    driver: bridge\n")

def apply_transformations(model):
	components = {}
	backend_name = None
	database_name = None
	load_balancer_name = None
	back_instances = 1
	for e in model.elements:
		if e.__class__.__name__ == 'Component':
			if e.type == 'backend':
				backend_name = e.name
			elif e.type == 'database':
				database_name = e.name
			elif e.type == 'load_balancer':
				load_balancer_name = e.name
				back_instances = e.instances
	for e in model.elements:
		if e.__class__.__name__ == 'Component':
			components[e.name] = e.type
			if e.type == 'database':
				generate_database(e.name)
			if e.type == 'backend':
				generate_backend(e.name, database=database_name)
			elif e.type == 'frontend':
				generate_frontend(e.name, backend=load_balancer_name)
			elif e.type == 'load_balancer':
				generate_load_balancer(e.name, backend=backend_name, instances=back_instances)
	generate_docker_compose(components, backend_name=backend_name, backend_instances=back_instances)