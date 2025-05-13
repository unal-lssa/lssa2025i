import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from typing import Optional
from DSL.IElement import IElement


class Network(IElement):
    def __init__(
        self,
        name: str,
        internal: bool = False,
        driver: Optional[str] = None,
    ):
        super().__init__(name)
        self._internal = internal
        self._driver = driver

    @property
    def internal(self) -> bool:
        return self._internal

    @property
    def driver(self) -> Optional[str]:
        return self._driver

    def accept(self, visitor: "IVisitor") -> None:
        visitor.visit_network(self)

    def validate(self) -> None:
        if self._driver is not None and not self._driver.strip():
            raise ValueError("Network driver cannot be empty string.")
