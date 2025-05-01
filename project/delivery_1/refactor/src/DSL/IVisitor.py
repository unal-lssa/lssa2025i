from abc import ABC, abstractmethod
from .Model import Model
from .Network import Network
from .StandardComponent import StandardComponent
from .LoadBalancer import LoadBalancer
from .Database import Database
from .ApiGateway import ApiGateway
from .Queue import Queue
from .Connector import Connector


class Visitor(ABC):
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
