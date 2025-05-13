import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from typing import List
from DSL.AComponent import AComponent
from DSL.Network import Network


class Queue(AComponent):
    def __init__(
        self,
        name: str,
        network: Network,
    ):
        super().__init__(name, network)

    def accept(self, visitor: "IVisitor") -> None:
        visitor.visit_queue(self)

    def validate(self) -> None:
        super().validate()
