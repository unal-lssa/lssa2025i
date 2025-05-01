from enum import Enum
from .AComponent import AComponent
from .Network import Network
from .IVisitor import IVisitor


class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    ELASTICSEARCH = "elasticsearch"
    MYSQL = "mysql"


class Database(AComponent):
    def __init__(
        self,
        name: str,
        database_type: DatabaseType,
        network: Network,
    ):
        super().__init__(name, network)
        self._database_type = database_type

    @property
    def database_type(self) -> DatabaseType:
        return self._database_type

    def accept(self, visitor: IVisitor) -> None:
        visitor.visit_database(self)
