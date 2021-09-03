"""general base class for all models"""
from abc import ABC, abstractmethod
from enum import Enum, auto


class ModelType(Enum):
    """Enumerate models"""
    ENTROPY = auto()


class DataModel(ABC):
    """The class serves as a base class for all data models, and server as an interface"""
    def __init__(self, model_type: ModelType):
        self.model_type = model_type

    @abstractmethod
    def update_model(self, new_data: bytes, **kwargs) -> None:
        """The method is responsible to update the model based on new observations.
        :param new_data: observation used to refine model
        :param kwargs: all other arguments which the model may require for the update
        """
        pass

    @abstractmethod
    def predict(self, data: bytes, **kwargs):
        """Responsible for making predictions regarding originally sent data, based on recent observations and model.
        :param data: recent observation regrading which a prediction is required.
        :param kwargs: all other arguments which the model may require to make predictions.
        """
        pass
