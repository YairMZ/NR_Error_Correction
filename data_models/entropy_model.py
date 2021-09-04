"""
Model which inheres structure bits based on entropy of previous buffers of assumed similar structure
"""
from .data_model import DataModel, ModelType
from utils.custom_exceptions import IncorrectBufferLength
import numpy as np
from utils.information_theory import prob, entropy


class EntropyModel(DataModel):
    """The model receives buffers of sme length, and assumes they share the same structure. The entropy of each element
    (bit or byte) in the buffer is calculated across samples (different buffers). The model assumes elements with low
    entropy are more likely to be be structural, and less likely to change.
    """
    def __init__(self, buffer_length: int, bitwise: bool = True):
        """
        :param buffer_length: buffer length in bytes
        :param bitwise: consider bitwise or bytewise elements
        """
        self.buffer_length: int = buffer_length
        self.bitwise: bool = bitwise
        self.data: np.ndarray = np.array([])
        self.distribution: np.ndarray = np.array([])
        self.entropy: np.ndarray = np.array([])
        super().__init__(ModelType.ENTROPY)

    def update_model(self, new_data: bytes, **kwargs) -> None:
        """The method is responsible to update the model based on new observations.
        :param new_data: observation used to refine model
        :param kwargs: all other arguments which the model may require for the update
        """
        if len(new_data) != self.buffer_length:
            raise IncorrectBufferLength()
        arr = np.array([np.frombuffer(new_data, dtype=np.uint8)]).T
        if self.bitwise:
            arr = np.unpackbits(arr, axis=0)
        self.data = arr if self.data.size == 0 else np.append(self.data, arr, axis=1)
        self.distribution = prob(self.data)
        self.entropy = entropy()

    def predict(self, data: bytes, **kwargs):
        """Responsible for making predictions regarding originally sent data, based on recent observations and model.
        :param data: recent observation regrading which a prediction is required.
        :param kwargs: all other arguments which the model may require to make predictions.
        """
        pass
