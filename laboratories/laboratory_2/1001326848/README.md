# Laboratory 2 - Modeling

Large Scale Software Architecture

Universidad Nacional de Colombia – 2025-I

## Student Information

Name: Santiago Suárez Suárez

Document ID: 1001326848

## How to Run the Project

1. Build the Docker image:

        docker build -t lssa-lab2 .

2. Run the container:

    - Linux / macOS

            docker run --rm -v "$PWD:/app" lssa-lab2

    - PowerShell (Windows)

            docker run --rm -v "$PWD:/app" lssa-lab2

    This process will generate the **skeleton** folder.

3. Navigate into the folder:

        cd skeleton

4. Start the services and scale the backend to 5 instances:

        docker compose up --build -d --scale lssa_be=5

## Verifying the Setup

To confirm that the services are running:

1. Use `docker ps` to check that all containers are up.

2. Ensure the frontend is accessible (usually on port 8002).

3. The frontend has been updated to display the container ID handling the request. Since the load balancer distributes requests across multiple backend instances, this allows you to verify that load balancing is working correctly.

![frontend](assets/frontend.png)

## Architecture C&C Diagram

![architecture-diagram](assets/c-c.png)

## Changes Introduced

1. arch.tx

    - Added a new component type: loadbalancer

2. model.arch

    - Defined a new component: lssa_lb (type: loadbalancer)

    - Updated connectors to reflect the new architecture flow:
    frontend → loadbalancer → backend → database

3. transformations.py

    - Implemented the transformation logic for generating the loadbalancer component.

    - Configured the load balancer using Nginx, routing traffic to all backend instances dynamically.
