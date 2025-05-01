from typing import List
from .AElement import AElement
from .IVisitor import IVisitor


class Model:
    """Model class representing a DSL model."""

    def __init__(self, elements: List[AElement]):
        self._elements: List[AElement] = elements

    @property
    def elements(self) -> List[AElement]:
        """All elements (networks, components, connectors) in the architecture."""
        return list(self._elements)

    def validate(self) -> None:
        """Validate all contained elements."""
        for elem in self._elements:
            elem.validate()

    def accept(self, visitor: IVisitor) -> None:
        """Traverse elements with a visitor."""
        visitor.visit_model(self)
        for elem in self._elements:
            elem.accept(visitor)
