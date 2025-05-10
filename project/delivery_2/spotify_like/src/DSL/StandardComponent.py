import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from enum import Enum
from DSL.AComponent import AComponent
from DSL.Network import Network


class StandardComponentType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    BUCKET = "bucket"
    CDN = "cdn"
    CACHE = "cache"


class StandardComponent(AComponent):
    def __init__(self, name: str, comp_type: StandardComponentType, network: Network):
        super().__init__(name, network)
        self._type = comp_type

    @property
    def type(self) -> StandardComponentType:
        return self._type

    def accept(self, visitor: "IVisitor") -> None:
        visitor.visit_standard_component(self)

    def validate(self):
        super().validate()
        if not isinstance(self.type, StandardComponentType):
            raise ValueError("Invalid standard component type.")
