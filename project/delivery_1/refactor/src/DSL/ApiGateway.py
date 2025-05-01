from typing import List
from .AComponent import AComponent
from .Network import Network
from .IVisitor import IVisitor


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

    def accept(self, visitor: IVisitor) -> None:
        visitor.visit_api_gateway(self)
