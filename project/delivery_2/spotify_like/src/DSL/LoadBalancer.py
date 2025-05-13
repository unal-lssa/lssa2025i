import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from DSL.AComponent import AComponent
from DSL.Network import Network


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
        self._targets = [target]

    @property
    def instance_count(self) -> int:
        return self._instance_count

    @property
    def targets(self) -> list[AComponent]:
        return self._targets

    @targets.setter
    def targets(self, targets: list[AComponent]) -> None:
        self._targets = list(targets)

    def accept(self, visitor: "IVisitor") -> None:
        visitor.visit_load_balancer(self)

    def validate(self) -> None:
        super().validate()
        if self._instance_count <= 0:
            raise ValueError(
                f"LoadBalancer {self.name} must have a positive instance count."
            )
        for target in self._targets:
            if not isinstance(target, AComponent):
                raise TypeError(
                    f"LoadBalancer {self.name} target must be an AComponent."
                )
