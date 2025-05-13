import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from DSL.AComponent import AComponent
from DSL.StandardComponent import StandardComponent
from DSL.Queue import Queue


class NetworkOrchestrator:
    START_PORT = 3000
    FRONTEND_PORT = 80

    def __init__(self):
        self.next_port = self.START_PORT
        self.assigned_ports: dict[str, int | list[int]] = {}

    def register_component(self, component: AComponent) -> int:
        """
        Register a component and assign it a port.
        """
        if component.name in self.assigned_ports:
            return self.assigned_ports[component.name]

        if isinstance(component, StandardComponent):
            # If the component is a frontend, assign it the frontend port
            if component.type == "frontend":
                assigned_port = self.FRONTEND_PORT
            else:
                # Otherwise, assign the next available port
                assigned_port = self.next_port
        elif isinstance(component, Queue):
            # For queues, assign a 2 to 1 mapping of ports
            assigned_port = [self.next_port, self.next_port + 1]
            self.next_port += 2
        else:
            assigned_port = self.next_port
        self.assigned_ports[component.name] = assigned_port
        self.next_port += 1
        return assigned_port

    def get_assigned_port(self, component: AComponent) -> int:
        """
        Get the assigned port for a component.
        """
        if component.name in self.assigned_ports:
            return self.assigned_ports[component.name]
        else:
            return self.register_component(component)
