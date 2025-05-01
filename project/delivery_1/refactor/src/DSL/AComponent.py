from abc import ABC
from .AElement import AElement
from .Network import Network


class AComponent(AElement, ABC):
    def __init__(self, name: str, network: Network):
        super().__init__(name)
        self._network = network

    @property
    def network(self) -> Network:
        return self._network

    def validate(self) -> None:
        # Ensure network association exists
        if self._network is None:
            raise ValueError(f"Component '{self.name}' must belong to a network.")
