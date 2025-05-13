# Spotify-like System Architecture Generator

This project utilizes a model-driven approach to automate the initial architectural design and generation of a skeleton for a Spotify-like music streaming platform. By defining the system's structure and components using a Domain-Specific Language (DSL) and a metamodel, transformation rules are applied to automatically generate a prototype.

## Authors

- Juan Andres Orozco Velandia
- Juan Esteban Hunter Malaver
- Carlos Santiago Sandoval Casallas
- Camilo Andres Cuello Romero
- Lucas Peña Salas
- Santiago Restrepo

## 1. Software System Context

The system designed is a representation of a music streaming platform, similar in concept to Spotify. Architecturally, it is designed to enable key functionalities such as browsing and searching music tracks, managing playlists, user authentication, and handling music files. The proposed architecture is capable of supporting a large number of users concurrently accessing and streaming content.

Based on the categories of large-scale software systems studied, this system is primarily classified under the category of Large Number of Concurrent Operations. This is because a music streaming platform is characterized by a high volume of simultaneous user interactions, including audio streaming, catalog searching, playlist management, and handling user requests. The ability to efficiently manage and respond to thousands or millions of concurrent user sessions is a critical architectural driver. While it also deals with a Large Volume of Data (the music catalog and user data) and involves Distribution (across various services), the main challenge and defining characteristic for this initial architectural design is the need to support a high degree of concurrency.

## 2. Architectural Style

The chosen architectural style for this system is **Microservices**.

The Microservices style is well-suited for systems requiring the handling of a large number of concurrent operations due to several key advantages:

* **Scalability:** Individual services (like the Catalog Service, User Service, Playlist Service) can be scaled independently based on their specific load. Services experiencing high concurrent demand can have more instances deployed without affecting less-loaded services. This is crucial for handling fluctuating user activity in a streaming platform.
* **Resilience:** The failure of one service is less likely to affect the entire system. If the Playlist Service experiences issues, users can still stream music and access other functionalities, improving overall system availability under high load or partial failures.
* **Maintainability and Agility:** Smaller, independently deployable services are easier to develop, test, and deploy. This allows for faster iteration and updates, which is beneficial in a dynamic platform like a music service.
* **Technology Diversity:** Different services can use the best technology stack for their specific needs (e.g., a NoSQL database for flexible playlist data, a relational DB for user data, Elasticsearch for search), although in this skeleton, we use simplified implementations.

While Microservices introduce complexity in terms of management and inter-service communication, the benefits in terms of scalability and resilience for handling a large number of concurrent operations outweigh these drawbacks for this type of large-scale system.

## Diagram
![Architecture Diagram](SpotifyLikeDiag.png)

## Components

- **Frontend**: Simple Node.js/Express web interface
- **Backend**: Simple Flask API service
- **Database**: Support for MySQL, MongoDB, PostgreSQL, and Elasticsearch
- **LoadBalancer**: Nginx load balancer
-  **CDN**: Nginx-based caching layer responsible for storing and serving song files efficiently to users.
-  **LocalStorage (S3 Emulation)**: Localstack-based S3-compatible storage service used to emulate AWS S3 buckets during development, enabling local upload, retrieval, and management of song files.
- **Music Storage Bucket**: Specific S3 bucket inside the LocalStorage instance dedicated to storing and organizing user-uploaded songs for retrieval by the CDN and other system components.
- **API Gateway**: Simple FastAPI API gateway
- **Queue**: A messaging broker that is used for communication between services in charge of receiving and asynchronous uploading of songs to the S3 bucket.


## Metamodel
```
Model:
    'architecture' ':'
        elements*=Element
;

Element:
    Network | Component | Connector
;

Network:
    'network' name=ID '{'
        'internal' '=' internal=BOOL
    '}'
;

Component:
    LoadBalancer | StandardComponent | Database | ApiGateway | Queue
;

LoadBalancer:
    'component' 'loadbalancer' name=ID instanceCount=INT target=[Component]
        'network' network=[Network]
;

StandardComponentType:
    'frontend' | 'backend' | 'bucket' | 'cdn' | 'cache'
;

StandardComponent:
    'component' type=StandardComponentType name=ID
        'network' network=[Network]
;

Database:
    'component' 'db' name=ID databaseType=DatabaseType
        'network' network=[Network]
;

DatabaseType:
    'postgresql' | 'mongodb' | 'elasticsearch' | 'mysql'
;

ApiGateway:
    'component' 'api_gateway' name=ID
        'auth' auth=[Component]
        'networks' networks+=[Network][',']
;

Queue:
    'component' 'queue' name=ID
        'network' network=[Network]
;

ConnectorType:
    'http' | 'db_connector' | 'queue_connector'
;

Connector:
    'connector' type=ConnectorType from=[Component] '->' to=[Component]
;
```

## Elements
- **Component**: Represents a component in the architecture. It can be a standard component, load balancer, or database.
- **Connector**: Represents a connection link between two components. It can be an HTTP connection, database connection, or Kafka connection.

## Component Types
- **StandardComponent**: Represents a basic deployable service. It can be a frontend, backend, bucket, CDN, or queue.
- **LoadBalancer**: It can be configured with an instance count and a target component to distribute traffic accross multiple instancers of target `Component`.
- **Database**: It can be configured with a specific database type.
- **ApiGateway**: API gateway component that proxies requests to the backend components.



## Connectors

The architecture supports the following connection types:

- **http**: HTTP connection between components (e.g., frontend to backend)
- **db_connector**: Database connection (e.g., backend to database)
- **kafka_connector**: Kafka connection for event streaming (A logic for matching producer and consumer services is included in the connectors)

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


## Metamodel
- **Model**
    ```
    Model:
    'architecture' ':'
        elements*=Element;
    ```
   The root structure of the architecture. It starts with the keyword architecture and contains a collection of Elements that define the complete system model.

- **Element:**
   ```
      Element:
         Component | Connector ;
   ```
   Base structure of the architecture, representing either a Component (active entity) or a Connector (interaction link between components).

- **Component:**
   ```
      Component:
         LoadBalancer | StandardComponent | Database | ApiGateway ;
   ```
   Abstract definition that groups different types of system elements, such as LoadBalancer, StandardComponent, Database, and ApiGateway.

- **StandardComponent:**

   ```
      StandardComponent:
         'component' type=StandardComponentType name=ID;
   ```
   A basic system component defined by a type (e.g., frontend, backend, bucket, cdn, or queue) and an identifying name. Used to model common system units.

- **StandardComponentType:**
   ```
      StandardComponentType:
         'frontend' | 'backend' | 'bucket' | 'cdn' | 'queue';
   ```
   Enumeration of the available types for StandardComponent, allowing specification as a frontend, backend, bucket, cdn, or queue.


## Transformation Rules:
- **Bucket Transformation Rule**:
This transformation generates the structure for a bucket service based on LocalStack S3. It creates a folder containing:

   1. A Dockerfile that builds a container from the localstack/localstack:s3-latest image, installs necessary tools (awscli, awscli-local), and sets up initialization scripts.

   2. An init-bucket.sh script that automatically creates a bucket named music-storage and uploads an initial song.mp3 file.

   3. A helper function to move external files into the bucket structure, ensuring the test song is available during container initialization.

   This transformation allows seamless simulation of an S3 environment for local development and testing.

- **CDN Transformation Rule**:
This transformation generates the structure for a content delivery service (CDN) using an Nginx proxy server.
It creates a folder containing:

   1. A nginx.conf configuration that sets up a proxy to forward requests to the music_storage service (LocalStack S3) and configures a local cache (proxy_cache) to improve response times and handle stale content.

   2. A Dockerfile that builds a container from the nginx:alpine image, copying the custom configuration and launching Nginx.

   This transformation enables caching of static content (like songs) and reduces the load on the underlying storage by serving frequently accessed resources directly from the cache.

- **Queue Transformation Rule**:
- This transformation generates the structure for a queue service using Kafka. It creates a folder containing:

   1. A Dockerfile that builds a container from the confluentinc/cp-kafka and confluentinc/cp-zookeeper images, setting up the necessary environment variables for Kafka and Zookeeper.

   2. A docker-compose.yml file that defines the Kafka and Zookeeper services, ensuring they are started together.

   3. Analysis of connectors in the model to adapt the backend services according to their connection with the queue.

   This transformation allows for asynchronous communication between services, enabling efficient handling of events and messages in the system.

- **Frontend Transformation Rule**:
This transformation generates the structure for the user interface component of the system. It creates a folder containing:

    1.  `index.html`: The main landing page of the application.
    2.  `player.html`: A basic music player interface.
    3.  `app.js`: A simple Node.js/Express server to serve the static HTML files and other assets.
    4.  `package.json`: Defines the Node.js project and its dependencies (Express).
    5.  `Dockerfile`: Specifies how to build the container image for the frontend service.

    This transformation provides a basic web presence for the system, capable of displaying static content and acting as the entry point for user interaction. It is configured to fetch music files from an external URL, simulating interaction with the CDN or storage service.

## Usage

1. Define your architecture in `model.arch`
2. At the spotify_like directory run this command:
   ```
   docker build -t app_delivery2 .
   ```
3. Now build the docker container to execute the program and generate the modeled software system.:
   ```
   docker run --rm -v "$PWD:/app" app_delivery2
   ```
4. The generated skeleton will be available in the `skeleton` directory

5. To run the system:
   ```
   cd skeleton
   docker-compose up --build

## Example Architecture

```
architecture:
    component frontend app_fe
    component backend app_be
    component db app_db mongodb

    connector http app_fe -> app_be
    connector db_connector app_be -> app_db
    component bucket music_storage
    component cdn songs_cdn
```

This defines a frontend that connects to a backend, which in turn connects to a MongoDB database.

# Testing the connections
To test the connections, you can use the following commands:

``` bash
curl --location 'localhost:8007/user'
```
``` bash
curl --location 'localhost:8007/playlist'
```
``` bash
curl --location 'localhost:8007/auth'
```
``` bash
curl --location 'localhost:8007/catalog
```
This commands will return some basic information about the backend and the database connection.

Example output:
``` json
{"status_code":200,"content":{"database_connection":"success","message":"Hello World from Backend","type":"PostgreSQL"}}
```
