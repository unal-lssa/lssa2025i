import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from abc import ABC
from DSL.IElement import IElement
from DSL.Network import Network


class AComponent(IElement, ABC):
    def __init__(self, name: str, network: Network):
        super().__init__(name)
        self._network = network

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def network(self) -> Network:
        return self._network

    def validate(self) -> None:
        # Ensure network association exists
        if self._network is None:
            raise ValueError(f"Component '{self.name}' must belong to a network.")
        if not isinstance(self._network, Network):
            raise TypeError(
                f"Network must be of type 'Network', got {type(self._network).__name__}."
            )

        # Ensure the component name is not empty
        if not self.name:
            raise ValueError("Component name cannot be empty.")
