from typing import List
from .IElement import IElement
from .IVisitor import IVisitor


class Model:
    """Model class representing a DSL model."""

    def __init__(self, elements: List[IElement]):
        self._elements: List[IElement] = elements

    @property
    def elements(self) -> List[IElement]:
        """All elements (networks, components, connectors) in the architecture."""
        return list(self._elements)

    def validate(self) -> None:
        """Validate all contained elements."""
        for elem in self._elements:
            if not callable(getattr(elem, "validate", None)):
                raise TypeError(f"Element {elem} does not have a validate method.")
            elem.validate()

        # Ensure no duplicate elements
        names = [elem.name for elem in self._elements]
        duplicates = set(name for name in names if names.count(name) > 1)
        if duplicates:
            raise ValueError(f"Duplicate elements found: {', '.join(duplicates)}")

    def accept(self, visitor: IVisitor) -> None:
        """
        Traverse elements with a visitor. You can use different Visitor implementations:
        - One visitor writes per-component files (Dockerfile, app.py) by handling visit_standard_component, visit_database, etc.
        - Another visitor collects service definitions into a shared docker-compose structure in visitor.visit_model or visit_network, then finalizes in visitor.post_visit_model.
        """
        visitor.visit_model(self)
        for elem in self._elements:
            if not callable(getattr(elem, "accept", None)):
                raise TypeError(f"Element {elem} does not have an accept method.")
            elem.accept(visitor)

        if hasattr(visitor, "post_visit_model"):
            visitor.post_visit_model(self)
