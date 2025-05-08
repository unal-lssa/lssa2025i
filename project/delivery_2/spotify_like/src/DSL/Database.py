import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from enum import Enum
from DSL.AComponent import AComponent
from DSL.Network import Network


class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    ELASTICSEARCH = "elasticsearch"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"


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

    def accept(self, visitor: "IVisitor") -> None:
        visitor.visit_database(self)

    def validate(self):
        super().validate()
        if not isinstance(self.database_type, DatabaseType):
            raise ValueError("Invalid database type.")
