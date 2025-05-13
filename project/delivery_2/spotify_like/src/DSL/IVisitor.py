import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from abc import ABC, abstractmethod
from DSL.Model import Model
from DSL.Network import Network
from DSL.StandardComponent import StandardComponent
from DSL.LoadBalancer import LoadBalancer
from DSL.Database import Database
from DSL.ApiGateway import ApiGateway
from DSL.Queue import Queue
from DSL.Connector import Connector


class IVisitor(ABC):
    @abstractmethod
    def visit_model(self, model: Model) -> None:
        pass

    @abstractmethod
    def visit_network(self, network: Network) -> None:
        pass

    @abstractmethod
    def visit_standard_component(self, comp: StandardComponent) -> None:
        pass

    @abstractmethod
    def visit_load_balancer(self, lb: LoadBalancer) -> None:
        pass

    @abstractmethod
    def visit_database(self, db: Database) -> None:
        pass

    @abstractmethod
    def visit_api_gateway(self, ag: ApiGateway) -> None:
        pass

    @abstractmethod
    def visit_queue(self, q: Queue) -> None:
        pass

    @abstractmethod
    def visit_connector(self, conn: Connector) -> None:
        pass
