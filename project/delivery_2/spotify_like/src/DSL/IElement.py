from abc import abstractmethod, ABCMeta


class IElement(metaclass=ABCMeta):
    """Abstract base class for all elements in the DSL."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        """Unique identifier of the element."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the element."""
        self._name = value

    @abstractmethod
    def accept(self, visitor: "IVisitor") -> None:
        """Accept a visitor (for generation, validation, etc.)."""
        pass

    @abstractmethod
    def validate(self) -> None:
        """Perform semantic validation of this element."""
        pass
