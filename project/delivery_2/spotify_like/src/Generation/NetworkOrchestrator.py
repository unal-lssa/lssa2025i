import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from DSL.AComponent import AComponent


class NetworkOrchestrator:
    START_PORT = 3000

    def __init__(self):
        self.next_port = self.START_PORT
        self.assigned_ports: dict[str, dict] = {}

    def register_component(self, component: AComponent) -> int:
        """
        Register a component and assign it a port.
        """
        if component.name in self.assigned_ports:
            return self.assigned_ports[component.name]

        assigned_port = self.next_port
        self.assigned_ports[component.name] = assigned_port
        self.next_port += 1
        return assigned_port
