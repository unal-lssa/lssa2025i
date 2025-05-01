from enum import Enum
from .AElement import AElement
from .AComponent import AComponent
from .IVisitor import IVisitor


class ConnectorType(Enum):
    HTTP = "http"
    DB_CONNECTOR = "db_connector"
    QUEUE_CONNECTOR = "queue_connector"


class Connector(AElement):
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
        # Example: ensure from/to are not the same
        if self._from is self._to:
            raise ValueError("Connector cannot link a component to itself.")
