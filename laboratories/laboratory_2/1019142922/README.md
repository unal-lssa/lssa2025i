# Lab 2

Juan Bernardo Benavides Rubio

## Load balancing

This model extends the given model by adding the possibility of introducing a load balancer
in between the frontend and the backend. The load balancer is defined using Nginx and
Docker's DNS resolver.

You can add the load balancer as a component in the model: `component load_balancer <name>`

Additionally, in order for the balancer to actually do something it is possible to add
an optional parameter to the backend defining the number of replicas you want (default is 1):
`component backend <name> <number_of_replicas>`.
