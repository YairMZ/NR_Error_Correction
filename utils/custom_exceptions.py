"""My custom exceptions used throughout the project"""
from typing import Any


class NonUint8(Exception):
    """Exception is raised if a function is given an  incompatible int argument where an uint8 is expected."""
    def __init__(self, *args: Any):
        """if argument are passed, the first is assumed to be the value passed and the second is the error message"""
        self.value = args[0] if args else None
        self.message = args[1] if len(args) > 1 else "Value is not uint8"
        super().__init__(self.message)


class IncorrectBufferLength(ValueError):
    """Raised when a buffer doesn't meet the expected length"""
    pass


class UnsupportedDtype(Exception):
    """Raised when a function receives a ndarray with supported dtype"""
    pass
