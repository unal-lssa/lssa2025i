import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from enum import Enum
from DSL.IElement import IElement
from DSL.AComponent import AComponent
from DSL.Queue import Queue
from DSL.StandardComponent import StandardComponentType


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
    def from_comp(self) -> AComponent:
        return self._from

    @from_comp.setter
    def from_comp(self, value: AComponent) -> None:
        self._from = value
        self.name = f"{self._type.value}:{self._from.name}->{self._to.name}"

    @property
    def to_comp(self) -> AComponent:
        return self._to

    @to_comp.setter
    def to_comp(self, value: AComponent) -> None:
        self._to = value
        self.name = f"{self._type.value}:{self._from.name}->{self._to.name}"

    @property
    def type(self) -> ConnectorType:
        return self._type

    def accept(self, visitor: "IVisitor") -> None:
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
        if self._type == ConnectorType.QUEUE_CONNECTOR:
            if not isinstance(self._to, Queue) and not isinstance(self._from, Queue):
                raise ValueError(
                    "QUEUE_CONNECTOR can only connect to queue components."
                )
