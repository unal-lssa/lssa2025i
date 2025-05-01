from enum import Enum
from .IElement import IElement
from .AComponent import AComponent
from .IVisitor import IVisitor


class ConnectorType(Enum):
    HTTP = "http"
    DB_CONNECTOR = "db_connector"
    QUEUE_CONNECTOR = "queue_connector"


class Connector(IElement):
    def __init__(
        self,
        from_comp: AComponent,
        to_comp: AComponent,
        conn_type: ConnectorType,
    ):
        # auto-generate a name
        name = f"{conn_type.value}:{from_comp.name}->{to_comp.name}"
        super().__init__(name)
        self._from = from_comp
        self._to = to_comp
        self._type = conn_type

    @property
    def from_component(self) -> AComponent:
        return self._from

    @property
    def to_component(self) -> AComponent:
        return self._to

    @property
    def type(self) -> ConnectorType:
        return self._type

    def accept(self, visitor: IVisitor) -> None:
        visitor.visit_connector(self)

    def validate(self) -> None:
        # Ensure from/to are not the same
        if self._from is self._to:
            raise ValueError("Connector cannot link a component to itself.")

        # Ensure from/to are of compatible types
        if not isinstance(self._from, AComponent) or not isinstance(
            self._to, AComponent
        ):
            raise TypeError("Both from and to must be AComponent instances.")

        # Ensure the connector type is valid
        if not isinstance(self._type, ConnectorType):
            raise ValueError("Invalid connector type.")

        # Ensure the connector type is compatible with the components
        if self._type == ConnectorType.DB_CONNECTOR:
            if not hasattr(self._to, "database_type"):
                raise ValueError(
                    "DB_CONNECTOR can only connect to a database component."
                )
            elif hasattr(self._from, "database_type"):
                raise ValueError("DB_CONNECTOR cannot connect two database components.")
        elif self._type == ConnectorType.QUEUE_CONNECTOR:
            if not hasattr(self._to, "queue_type") or not hasattr(
                self._from, "queue_type"
            ):
                raise ValueError(
                    "QUEUE_CONNECTOR can only connect to queue components."
                )
