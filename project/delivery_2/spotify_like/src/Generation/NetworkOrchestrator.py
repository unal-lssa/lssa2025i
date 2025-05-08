import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from DSL.AComponent import AComponent


class NetworkOrchestrator:
    START_PORT = 3000
    FRONTEND_PORT = 80

    def __init__(self):
        self.next_port = self.START_PORT
        self.assigned_ports: dict[str, dict] = {}

    def register_component(self, component: AComponent) -> int:
        """
        Register a component and assign it a port.
        """
        if component.name in self.assigned_ports:
            return self.assigned_ports[component.name]

        if isinstance(component, AComponent):
            # If the component is a frontend, assign it the frontend port
            if component.type == "frontend":
                assigned_port = self.FRONTEND_PORT
            else:
                # Otherwise, assign the next available port
                assigned_port = self.next_port
        else:
            assigned_port = self.next_port
        self.assigned_ports[component.name] = assigned_port
        self.next_port += 1
        return assigned_port
