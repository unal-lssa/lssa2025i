import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

import yaml
from DSL.IVisitor import IVisitor
from DSL.Model import Model
from DSL.StandardComponent import StandardComponent, StandardComponentType
from DSL.Database import Database, DatabaseType
from DSL.Queue import Queue
from DSL.LoadBalancer import LoadBalancer
from DSL.ApiGateway import ApiGateway
from DSL.Network import Network
from DSL.Connector import Connector, ConnectorType
from DSL.AComponent import AComponent

from Generation.NetworkOrchestrator import NetworkOrchestrator

from typing import Optional


class DockerComposeWriterVisitor(IVisitor):
    def __init__(self, output_dir: str = "skeleton", network_orchestrator=None):
        self._output = output_dir
        self.net_orch = network_orchestrator or NetworkOrchestrator()
        self._model: Optional[Model] = None
        self._services: dict[str, dict] = {}
        self._networks: dict[str, dict] = {}
        os.makedirs(self._output, exist_ok=True)

    def _get_dependencies(self, comp: AComponent) -> list[str]:
        dependencies = []
        for elem in self._model.elements:
            if not isinstance(elem, Connector):
                continue
            if elem.to_comp.name != comp.name and elem.from_comp.name != comp.name:
                continue

            match elem.type:
                case ConnectorType.QUEUE_CONNECTOR:
                    # Bi-directional connector
                    ref = (
                        elem.to_comp
                        if elem.from_comp.name == comp.name
                        else elem.from_comp
                    )
                    dependencies.append(ref.name)
                case ConnectorType.HTTP:
                    dependencies.append(elem.to_comp.name)
                case ConnectorType.DB_CONNECTOR:
                    dependencies.append(elem.to_comp.name)

        # Remove duplicates and self references
        dependencies = list(set(dependencies))
        dependencies = [dep for dep in dependencies if dep != comp.name]
        return dependencies

    def visit_model(self, model: Model):
        self._model = model
        self._services = {}
        self._networks = {}
        self._volumes = {}

    def visit_network(self, network: Network) -> None:
        conf: dict = {}
        if network.internal:
            conf["internal"] = True
        if network.driver:
            conf["driver"] = network.driver or "bridge"
        self._networks[network.name] = conf

    def visit_standard_component(self, comp: StandardComponent) -> None:
        if comp.type == StandardComponentType.CACHE:
            self._services[comp.name] = {
                "image": "redis:latest",
                "networks": [comp.network.name],
                "container_name": comp.name,
            }
            return

        svc: dict = {
            "build": {
                "context": f"./{comp.name}",
                "dockerfile": "Dockerfile",
            },
            "networks": [comp.network.name],
            "container_name": comp.name,
            "depends_on": self._get_dependencies(comp),
        }

        if not svc["depends_on"]:
            del svc["depends_on"]

        if comp.type == StandardComponentType.FRONTEND:
            port = self.net_orch.get_assigned_port(comp)
            svc["ports"] = [
                f"{port}:80"
            ]  # This port is the default for frontend service
        self._services[comp.name] = svc

    def visit_database(self, db: Database) -> None:
        self._services[db.name] = {
            "image": DatabaseType.get_docker_image(db.database_type),
            "networks": [db.network.name],
            "environment": DatabaseType.get_environment_variables(db.database_type),
            "container_name": db.name,
            "volumes": [],
        }

        entrypoint = DatabaseType.get_entrypoint(db)
        if entrypoint:
            self._services[db.name]["volumes"].append(entrypoint)
            self._volumes[db.name] = {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": f"./{self._output}/{db.name}/data",
                },
            }
        else:
            del self._services[db.name]["volumes"]

    def visit_queue(self, q: Queue) -> None:
        ports = self.net_orch.get_assigned_port(q)  # This is a 2 to 1 mapping of ports
        self._services[q.name] = {
            "image": "rabbitmq:3-management",
            "networks": [q.network.name],
            "ports": [f"{ports[0]}:5672", f"{ports[1]}:15672"],
            "container_name": q.name,
            "volumes": [
                f"./{self._output}/{q.name}/data:/var/lib/rabbitmq",
                f"./{self._output}/{q.name}/config:/etc/rabbitmq",
            ],
        }

        self._volumes[q.name] = {
            "driver": "local",
            "driver_opts": {
                "type": "none",
                "o": "bind",
                "device": f"{self._output}/{q.name}/data",
            },
        }

    def visit_load_balancer(self, lb: LoadBalancer) -> None:
        self._services[lb.name] = {
            "image": "nginx:latest",
            "networks": [lb.network.name],
            "depends_on": [target.name for target in lb.targets],
            "container_name": lb.name,
        }

    def visit_api_gateway(self, ag: ApiGateway) -> None:
        self._services[ag.name] = {
            "image": "nginx:latest",
            "networks": [net.name for net in ag.networks],
            "depends_on": self._get_dependencies(ag),
            "container_name": ag.name,
        }

    def visit_connector(self, conn: Connector) -> None:
        pass

    def post_visit_model(self, model: Model) -> None:
        compose = {
            "services": self._services,
            "networks": self._networks,
            "volumes": self._volumes,
        }

        path = os.path.join(self._output, "docker-compose.yml")
        with open(path, "w") as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)
