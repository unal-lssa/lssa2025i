from enum import Enum
from .AComponent import AComponent
from .Network import Network
from .IVisitor import IVisitor


class StandardComponentType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    BUCKET = "bucket"
    CDN = "cdn"


class StandardComponent(AComponent):
    def __init__(self, name: str, comp_type: StandardComponentType, network: Network):
        super().__init__(name, network)
        self._type = comp_type

    @property
    def type(self) -> StandardComponentType:
        return self._type

    def accept(self, visitor: IVisitor) -> None:
        visitor.visit_standard_component(self)

    def validate(self):
        super().validate()
        if not isinstance(self.type, StandardComponentType):
            raise ValueError("Invalid standard component type.")
