import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

import yaml
from DSL.IVisitor import IVisitor
from DSL.Model import Model
from DSL.StandardComponent import StandardComponent
from DSL.Database import Database
from DSL.Queue import Queue
from DSL.LoadBalancer import LoadBalancer
from DSL.ApiGateway import ApiGateway
from DSL.Network import Network
from DSL.Connector import Connector
from DSL.AComponent import AComponent

from typing import Optional


class DockerComposeWriterVisitor(IVisitor):
    def __init__(self, output_dir: str = "skeleton", network_orchestrator=None):
        self._services = {}
        self._output = output_dir
        self.net_orch = network_orchestrator
        os.makedirs(self._output, exist_ok=True)

    def visit_model(self, model: Model):
        pass

    def visit_standard_component(self, comp: StandardComponent) -> None:
        self._write_service(comp, image=None)

    def visit_database(self, db: Database) -> None:
        self._write_service(db, image=None)

    def visit_queue(self, q: Queue) -> None:
        self._write_service(q, image=None)

    def visit_load_balancer(self, lb: LoadBalancer) -> None:
        self._write_service(lb, image=None)

    def visit_api_gateway(self, ag: ApiGateway) -> None:
        self._write_service(ag, image=None)

    def visit_network(self, network: Network) -> None:
        pass

    def visit_connector(self, conn: Connector) -> None:
        pass

    def post_visit_model(self, model: Model) -> None:
        pass

    def _write_service(self, comp: AComponent, image: Optional[str]) -> None:
        pass
