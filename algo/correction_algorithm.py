"""Base class for all correction algorithms"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from data_models import DataModel
from typing import Any


class AlgorithmType(Enum):
    """Enumerate models"""
    STRUCTURE_BASED = auto()


class CorrectionAlgorithm(ABC):
    """The class serves as a base class for all correction algorithms, and serves as an interface"""
    def __init__(self, algo_type: AlgorithmType, data_model: DataModel):
        """
        :param algo_type: Every algorithm must have a type
        :param data_model: Every algorithm must be based on some underlying model for the data.
        """
        self.algo_type = algo_type
        self.model = data_model

    @abstractmethod
    def correct_data(self, data: bytes, **kwargs) -> tuple[bytes, Any]:
        """Attempt to correct data

        :param data: recent observation
        :param kwargs: all other arguments which the algorithm may require.
        :return: return a tuple containing a prediction as a bytes object and some confidence measure as second element.
        """
