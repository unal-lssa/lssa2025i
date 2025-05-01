from .AComponent import AComponent
from .Network import Network
from .IVisitor import IVisitor


class LoadBalancer(AComponent):
    def __init__(
        self,
        name: str,
        instance_count: int,
        target: AComponent,
        network: Network,
    ):
        super().__init__(name, network)
        self._instance_count = instance_count
        self._target = target

    @property
    def instance_count(self) -> int:
        return self._instance_count

    @property
    def target(self) -> AComponent:
        return self._target

    def accept(self, visitor: IVisitor) -> None:
        visitor.visit_load_balancer(self)
