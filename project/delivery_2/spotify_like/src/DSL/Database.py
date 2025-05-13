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

    @classmethod
    def get_docker_image(cls, db_type: str) -> str:
        match db_type.value:
            case cls.POSTGRESQL.value:
                return "postgres:latest"
            case cls.ELASTICSEARCH.value:
                return "elasticsearch:9.0.1"
            case cls.MYSQL.value:
                return "mysql:latest"
            case cls.MONGODB.value:
                return "mongo:latest"
            case _:
                raise ValueError(f"Unknown database type: {db_type}")

    @classmethod
    def get_environment_variables(cls, db_type: str) -> dict:
        match db_type.value:
            case cls.POSTGRESQL.value:
                return {"POSTGRES_USER": "user", "POSTGRES_PASSWORD": "password"}
            case cls.ELASTICSEARCH.value:
                return {"ELASTIC_PASSWORD": "password"}
            case cls.MYSQL.value:
                return {"MYSQL_ROOT_PASSWORD": "root_password"}
            case cls.MONGODB.value:
                return {
                    "MONGO_INITDB_ROOT_USERNAME": "root",
                    "MONGO_INITDB_ROOT_PASSWORD": "password",
                }
            case _:
                raise ValueError(f"Unknown database type: {db_type}")

    @classmethod
    def get_entrypoint(cls, db: "Database") -> str:
        db_type = db.database_type
        match db_type.value:
            case cls.POSTGRESQL.value:
                return f"./{db.name}/init.sql:/docker-entrypoint-initdb.d/init.sql"
            case cls.ELASTICSEARCH.value:
                return None
            case cls.MYSQL.value:
                return f"./{db.name}/init.sql:/docker-entrypoint-initdb.d/init.sql"
            case cls.MONGODB.value:
                return (
                    f"./{db.name}/init.js:/docker-entrypoint-initdb.d/init-mongo.js:ro"
                )
            case _:
                raise ValueError(f"Unknown database type: {db_type}")


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
