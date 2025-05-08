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

    def visit_model(self, model: Model):
        self._model = model

    def visit_network(self, network: Network) -> None:
        # This configuration is defined in the docker-compose file
        pass

    def visit_standard_component(self, comp: StandardComponent) -> None:
        if comp.type == StandardComponentType.BACKEND:
            self._write_backend_service(comp)
        elif comp.type == StandardComponentType.FRONTEND:
            pass  # TODO: Add frontend service
        elif comp.type == StandardComponentType.CDN:
            pass  # TODO: Write config files
        elif comp.type == StandardComponentType.BUCKET:
            pass  # TODO: Write config files

    def visit_database(self, db: Database) -> None:
        # Use the database docker image
        pass

    def visit_queue(self, q: Queue) -> None:
        # Use the queue docker image
        pass

    def visit_load_balancer(self, lb: LoadBalancer) -> None:
        pass  # TODO: Write config files

    def visit_api_gateway(self, ag: ApiGateway) -> None:
        pass  # TODO: Implement API Gateway

    def visit_connector(self, conn: Connector) -> None:
        pass  # TODO: Add connector injection

    def _write_backend_service(self, comp: AComponent) -> None:
        port = self.net_orch.register_component(comp)
        svc = os.path.join(self._output, f"{comp.name}")
        os.makedirs(svc, exist_ok=True)

        # Dockerfile
        df = [
            "FROM python:3.9-slim",
            "WORKDIR /app",
            "COPY requirements.txt .",
            "RUN pip install -r requirements.txt",
            "COPY app.py .",
            "CMD ['python','app.py']",
        ]
        with open(os.path.join(svc, "Dockerfile"), "w") as f:
            f.write("\n".join(df))

        # App code
        lines = [
            "from flask import Flask, jsonify",
            "\n",
            self.REPLACE_CONNECTION_STRING,
            self.REPLACE_IMPORT_STRING,
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
