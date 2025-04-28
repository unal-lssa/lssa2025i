# Spotify-like System Architecture Generator

This project provides a DSL (Domain-Specific Language) and transformation toolset to generate a skeleton for a Spotify-like application architecture.

## Overview

The system uses a model-driven approach to generate the necessary components and connections for a microservices architecture. The generated components are minimal "hello world" implementations.

## Diagram
![Architecture Diagram](SpotifyLikeDiag.png)

## Components

- **Frontend**: Simple Node.js/Express web interface
- **Backend**: Simple Flask API service 
- **Database**: Support for MySQL, MongoDB, PostgreSQL, and Elasticsearch
- **LoadBalancer**: Nginx load balancer
- **API Gateway**: Simple FastAPI API gateway


## Metamodel
```
Model:
    'architecture' ':'
        elements*=Element
;

Element:
    Component | Connector | Network
;

Component:
    LoadBalancer | StandardComponent | Database | ApiGateway
;

StandardComponent:
    'component' type=StandardComponentType name=ID
;

LoadBalancer:
    'component' 'loadbalancer' name=ID instanceCount=INT target=[Component]
;

StandardComponentType:
    'frontend' | 'backend' | 'bucket' | 'cdn' | 'queue'
;

Database:
    'component' 'db' name=ID databaseType=DatabaseType
;

DatabaseType:
    'postgresql' | 'mongodb' | 'elasticsearch'
;

ApiGateway:
    'component' 'api_gateway' name=ID auth=Component
;

Connector:
    'connector' type=ConnectorType from=[Component] '->' to=[Component]
;

ConnectorType:
    'http' | 'db_connector' | 'kafka_connector'
;

Network:
    'network' networkName=ID
;
```

## Elements
- **Component**: Represents a component in the architecture. It can be a standard component, load balancer, or database.
- **Connector**: Represents a connection link between two components. It can be an HTTP connection, database connection, or Kafka connection.
- **Network**: Represents a network configuration. 

## Component Types
- **StandardComponent**: Represents a basic deployable service. It can be a frontend, backend, bucket, CDN, or queue.
- **LoadBalancer**: It can be configured with an instance count and a target component to distribute traffic accross multiple instancers of target `Component`.
- **Database**: It can be configured with a specific database type.
- **ApiGateway**: API gateway component that proxies requests to the backend components.



## Connectors

The architecture supports the following connection types:

- **http**: HTTP connection between components (e.g., frontend to backend)
- **db_connector**: Database connection (e.g., backend to database)
- **kafka_connector**: Kafka connection for event streaming (placeholder)

## Database Support

The system supports multiple database types:
- **mysql**: Default MySQL database 
- **mongodb**: MongoDB NoSQL database
- **postgresql**: PostgreSQL relational database
- **elasticsearch**: Elasticsearch search engine

Example usage in model.arch:
```
component db app_db mongodb
```

## Connection Implementation

When a component is defined as the "from" side of a connector, appropriate code is generated:

- For **http** connectors: Basic HTTP client code is added to connect to the target service
- For **db_connector**: Connection code specific to the database type is added

## Usage

1. Define your architecture in `model.arch`
2. Run the generator:
   ```
   python generation.py
   ```
3. The generated skeleton will be available in the `skeleton` directory
4. To run the system:
   ``` bash
   cd skeleton
   docker-compose up --build
   ```

## Example Architecture

```
architecture:
    component frontend app_fe
    component backend app_be
    component db app_db mongodb

    connector http app_fe -> app_be
    connector db_connector app_be -> app_db
```

This defines a frontend that connects to a backend, which in turn connects to a MongoDB database.


# How to run
1. `docker build -t app_delivery1 .`
2. `docker run --rm -v "$(Get-Location):/app" app_delivery1`
3. `cd .\skeleton\ && docker compose up --build`
4. Go to `http://localhost:8006/` (frontend)