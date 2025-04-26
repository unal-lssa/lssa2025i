# Lab 3

Juan Bernardo Benavides Rubio

A tool for generating microservice architectures based on a declarative model. It creates all necessary components including frontend, backend, database, and an API gateway.

## Features

- Declarative architecture definition using a simple DSL
- Generates complete microservice components:
  - Frontend (static HTML/CSS/JS served by Nginx)
  - Backend (FastAPI services)
  - Database (MySQL)
  - API Gateway (FastAPI with authentication)
- Docker-based deployment
- Automatic service discovery and routing
- Configurable authentication methods

## Prerequisites

- Python 3.13 or higher
- Docker and Docker Compose

## Installation

### Using uv 

```bash
# Build the generator image
uv sync --locked
```

## Usage

1. Define your architecture in a `.arch` file:

```arch
architecture:
    component frontend web

    component backend api
    {
        endpoint users: GET "/users" auth api_key
        expose users as "/api/users"
    }

    component database db

    connector http web -> api
    connector db_connector api -> db
```

There is an example file in the `examples` directory

2. Generate the architecture:

```bash
uv run generate {path_to_model}
```

3. Run the generated architecture:

```bash
cd sekeleton
docker-compose up --build
```

## Project Structure

The generated project will have the following structure:

```
skeleton/
├── api_gateway/
│   ├── api_gateway.json
│   ├── main.py
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── Dockerfile
├── backend/
│   ├── main.py
│   ├── Dockerfile
│   └── pyproject.toml
├── database/
│   ├── init.sql
│   └── README.md
└── docker-compose.yml
```

With the actual services and names you define in your model.

## API Gateway

The API Gateway provides:
- Unified API access point
- Authentication handling
- Request routing
- CORS management

### Authentication

Currently supports:
- API Key authentication (dummy implementation)

