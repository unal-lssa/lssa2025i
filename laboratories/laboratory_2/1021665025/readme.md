# [LSSA_2025i] - Laboratory 2 - Modeling 

---

Name: Santiago Restrepo

Citizenship ID:  1021665025

Course: Large-Scale Software Architecture

Date: April 12, 2025

---

## Changes Added:

1.  **DSL Grammar Extension:** The Domain Specific Language (DSL) grammar defined in the `arch.tx` file was extended to include the `"load_balancer"` component type. This addition enables the specification of load balancers within the system architecture description.

2.  **System Architecture Modification:** The system architecture, as defined in the `model.arch` file, was modified to integrate a load balancer. This component has been strategically positioned between the frontend and a set of three backend servers. Each backend server is designed to process requests independently while maintaining a connection to a shared database.

3.  **Load Balancer Generation Implementation:** The `generate_load_balancer` function was implemented in the `transformations.py` file. This function aims to generate the necessary configuration files for the Nginx server, as well as the corresponding Dockerfile. This setup allows for the establishment of a load balancer using the default Round Robin request distribution algorithm.

4.  **Docker Compose Generation Update:** The `generate_docker_compose` function in the `transformations.py` file was updated to integrate the load balancer generation logic. This includes invoking the `generate_load_balancer` function and configuring an explicit dependency of the frontend component on the load balancer. This dependency ensures that the load balancer is operational before the frontend attempts to access the backend servers.
