import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

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

from .NetworkOrchestrator import NetworkOrchestrator

from .Templates.frontendTemplate import generate_frontend
from .Templates.apiGatewayTemplate import generate_api_gateway
from .Templates.bucketTemplate import generate_bucket, move_file
from .Templates.generateCDN import generate_cdn
from .Templates.generateLoadBalancer import generate_load_balancer
from .Templates.generateDatabase import generate_database
from .Templates.generateBackend import (
    get_auth_service_lines,
    get_import_dependencies,
    write_docker_file,
)

from typing import Optional


class CodeGeneratorVisitor(IVisitor):
    # DON'T USE THIS STRINGS IN YOUR CODE
    REPLACE_IMPORT_STRING = "###!IMPORT REPLACEMENT HERE!###"
    REPLACE_CONNECTION_STRING = "###!CONNECTION REPLACEMENT HERE!###"

    def __init__(self, output_dir: str = "skeleton"):
        self._output = output_dir
        self.net_orch = NetworkOrchestrator()
        self._model: Optional[Model] = None
        self.conn_list = []
        os.makedirs(self._output, exist_ok=True)

    @property
    def network_orchestrator(self):
        return self.net_orch

    def visit_model(self, model: Model):
        self._model = model
        for element in self._model.elements:
            if isinstance(element, Connector):
                self.conn_list.append(element)

    def visit_network(self, network: Network) -> None:
        # This configuration is defined in the docker-compose file
        pass

    def visit_standard_component(self, comp: StandardComponent) -> None:
        if comp.type == StandardComponentType.BACKEND:
            self._write_backend_service(comp)
        elif comp.type == StandardComponentType.FRONTEND:
            self._write_frontend_service(comp)
        elif comp.type == StandardComponentType.CDN:
            generate_cdn(comp.name, self._output)
        elif comp.type == StandardComponentType.BUCKET:
            move_file(
                os.path.join(os.path.dirname(__file__), "Templates", "song.mp3"),
                f"{self._output}/{comp.name}",
            )
            generate_bucket(comp.name, self._output)
        elif comp.type == StandardComponentType.CACHE:
            pass  ## This configuration is defined in the docker-compose file

    def visit_database(self, db: Database) -> None:
        # Get Port
        port = self.net_orch.register_component(db)

        # Generate the database
        generate_database(
            component=db,
            net_orch=self.net_orch,
            output_dir=self._output,
        )

    def visit_queue(self, q: Queue) -> None:
        # Use the queue docker image
        pass

    def visit_load_balancer(self, lb: LoadBalancer) -> None:
        generate_load_balancer(
            load_balancer=lb,
            net_orch=self.net_orch,
            output_dir=self._output,
        )

    def visit_api_gateway(self, ag: ApiGateway) -> None:
        # Get all connected components
        route_map = {}
        for conn in self._model.elements:
            if not isinstance(conn, Connector):
                continue
            if conn.from_comp.name == ag.name:
                port = self.net_orch.get_assigned_port(conn.to_comp)
                route_map[conn.to_comp.name] = port

        generate_api_gateway(ag.name, self._output, route_map)

    def visit_connector(self, conn: Connector) -> None:
        pass  # TODO: Add connector injection

    def _is_auth_service(self, comp: AComponent) -> bool:
        # Check if the component is an auth service
        for api_gateway in self._model.elements:
            if not isinstance(api_gateway, ApiGateway):
                continue
            if comp.name == api_gateway.auth.name:
                # Is directly connected to the api gateway
                return True
            elif isinstance(api_gateway.auth, LoadBalancer):
                # Check if the load balancer is connected to the current service
                for conn in self._model.elements:
                    if not isinstance(conn, Connector):
                        continue
                    if conn.from_comp.name == api_gateway.auth.name:
                        if conn.to_comp.name == comp.name:
                            return True
        return False

    def _write_backend_service(self, comp: AComponent) -> None:
        svc = os.path.join(self._output, f"{comp.name}")
        os.makedirs(svc, exist_ok=True)

        # Generate the docker file
        dependencies = get_import_dependencies(comp, self.conn_list.copy())
        write_docker_file(svc, dependencies)

        if self._is_auth_service(comp):
            auth_lines = get_auth_service_lines(
                comp, self.conn_list.copy(), self.net_orch
            )
            with open(os.path.join(svc, "app.py"), "w") as f:
                f.write(auth_lines)
            return

    def _write_frontend_service(self, comp: AComponent) -> None:
        generate_frontend(comp.name, self._output)
