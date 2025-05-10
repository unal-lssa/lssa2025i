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

from typing import Optional


class CodeGeneratorVisitor(IVisitor):
    # DON'T USE THIS STRINGS IN YOUR CODE
    REPLACE_IMPORT_STRING = "###!IMPORT REPLACEMENT HERE!###"
    REPLACE_CONNECTION_STRING = "###!CONNECTION REPLACEMENT HERE!###"

    def __init__(self, output_dir: str = "skeleton"):
        self._output = output_dir
        self.net_orch = NetworkOrchestrator()
        self._model: Optional[Model] = None
        os.makedirs(self._output, exist_ok=True)

    @property
    def network_orchestrator(self):
        return self.net_orch

    def visit_model(self, model: Model):
        self._model = model

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

    def _write_backend_service(self, comp: AComponent) -> None:
        port = self.net_orch.register_component(comp)
        svc = os.path.join(self._output, f"{comp.name}")
        os.makedirs(svc, exist_ok=True)

        req = [
            "flask",
        ]
        with open(os.path.join(svc, "requirements.txt"), "w") as f:
            f.write("\n".join(req))

        # Dockerfile
        df = [
            "FROM python:3.11-slim",
            "WORKDIR /app",
            "COPY . .",
            "RUN pip install -r requirements.txt",
            'CMD ["python", "app.py"]',
        ]
        with open(os.path.join(svc, "Dockerfile"), "w") as f:
            f.write("\n".join(df))

        # App code
        lines = [
            "from flask import Flask, jsonify",
            "\n",
            self.REPLACE_IMPORT_STRING,
            self.REPLACE_CONNECTION_STRING,
            "\n",
            "app=Flask(__name__)",
            "\n",
            "@app.route('/')",
            "def hello(): return jsonify({'msg':'Hola Mundo'})",
            "\n",
            "if __name__ == '__main__':",
            f"    app.run(host='0.0.0.0', port={port})",
        ]

        with open(os.path.join(svc, "app.py"), "w") as f:
            f.write("\n".join(lines))

    def _write_frontend_service(self, comp: AComponent) -> None:
        generate_frontend(comp.name, self._output)
