import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from typing import List
from DSL.AComponent import AComponent
from DSL.Network import Network


class ApiGateway(AComponent):
    def __init__(
        self,
        name: str,
        auth: AComponent,
        networks: List[Network],
    ):
        super().__init__(name, networks[0])  # primary net for gateway
        self._auth = auth
        self._networks = networks

    @property
    def auth(self) -> AComponent:
        return self._auth

    @property
    def networks(self) -> List[Network]:
        return list(self._networks)

    def accept(self, visitor: "IVisitor") -> None:
        visitor.visit_api_gateway(self)

    def validate(self) -> None:
        super().validate()
        if not isinstance(self.auth, AComponent):
            raise TypeError("Auth must be an instance of AComponent.")
        if not all(isinstance(net, Network) for net in self.networks):
            raise TypeError("All networks must be instances of Network.")
