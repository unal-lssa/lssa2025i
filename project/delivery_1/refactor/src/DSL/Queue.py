from typing import List
from .AComponent import AComponent
from .Network import Network
from .IVisitor import IVisitor


class Queue(AComponent):
    def __init__(
        self,
        name: str,
        partitions: int,
        replication: int,
        network: Network,
    ):
        super().__init__(name, network)
        self._partitions = partitions
        self._replication = replication

    @property
    def partitions(self) -> int:
        return self._partitions

    @property
    def replication(self) -> int:
        return self._replication

    def accept(self, visitor: IVisitor) -> None:
        visitor.visit_queue(self)

    def validate(self) -> None:
        super().validate()
        if not isinstance(self.partitions, int) or self.partitions <= 0:
            raise ValueError("Partitions must be a positive integer.")
        if not isinstance(self.replication, int) or self.replication <= 0:
            raise ValueError("Replication must be a positive integer.")
