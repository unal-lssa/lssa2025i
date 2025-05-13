import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from typing import List
from DSL.IElement import IElement
from DSL.Network import Network
from DSL.Database import Database
from DSL.Queue import Queue
from DSL.StandardComponent import StandardComponent
from DSL.LoadBalancer import LoadBalancer
from DSL.ApiGateway import ApiGateway
from DSL.Connector import Connector


class Model:
    """Model class representing a DSL model."""

    def __init__(self, elements: List[IElement]):
        self._elements: List[IElement] = elements

    @property
    def elements(self) -> List[IElement]:
        """All elements (networks, components, connectors) in the architecture."""
        return list(self._elements)

    def _accept_by_instance(self, visitor: "IVisitor", classType: type) -> None:
        """
        Accept a visitor for a specific class type.
        This is used to filter elements by their class type.
        """
        for elem in [e for e in self._elements if isinstance(e, classType)]:
            if not hasattr(elem, "accept"):
                raise TypeError(f"Element {elem} does not have an accept method.")
            elem.accept(visitor)

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

    def accept(self, visitor: "IVisitor") -> None:
        """
        Traverse elements with a visitor. You can use different Visitor implementations:
        - One visitor writes per-component files (Dockerfile, app.py) by handling visit_standard_component, visit_database, etc.
        - Another visitor collects service definitions into a shared docker-compose structure in visitor.visit_model or visit_network, then finalizes in visitor.post_visit_model.
        """

        # Call Order
        # 1. Model
        # 2. Network
        # 3. Database - Queue
        # 4. StandardComponent
        # 5. LoadBalancer
        # 6. ApiGateway
        # 7. Connector
        # 8. Post visit model
        visitor.visit_model(self)
        self._accept_by_instance(visitor, Network)
        self._accept_by_instance(visitor, Database)
        self._accept_by_instance(visitor, Queue)
        self._accept_by_instance(visitor, StandardComponent)
        self._accept_by_instance(visitor, LoadBalancer)
        self._accept_by_instance(visitor, ApiGateway)
        self._accept_by_instance(visitor, Connector)

        if hasattr(visitor, "post_visit_model"):
            visitor.post_visit_model(self)
