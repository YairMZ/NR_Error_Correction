"""
Model which inheres structure bits based on entropy of previous buffers of assumed similar structure
"""
from .data_model import DataModel, ModelType  # type: ignore
from utils.custom_exceptions import IncorrectBufferLength
import numpy as np
from utils.information_theory import prob, entropy
from utils.custom_exceptions import UnsupportedDtype
from typing import Union


class EntropyModel(DataModel):
    """The model receives buffers of sme length, and assumes they share the same structure. The entropy of each element
    (bit or byte) in the buffer is calculated across samples (different buffers). The model assumes elements with low
    entropy are more likely to be be structural, and less likely to change.
    """
    alphabet_size_dict = {"uint8": 256, "uint16": 65536, "uint32": 4294967296, "int8": 256, "int16": 65536,
                          "int32": 4294967296}
    data_type = {"uint8": np.uint8, "uint16": np.uint16, "uint32": np.uint32, "int8": np.int8, "int16": np.int16,
                 "int32": np.int32}

    def __init__(self, buffer_length: int, bitwise: bool = True, window_length: Union[int, None] = None,
                 element_type: str = "uint8"):
        """
        :param buffer_length: buffer length in bytes
        :param bitwise: consider bitwise or bytewise elements
        :param window_length: number of last messages to consider when evaluating distribution and entropy
        :param element_type: a supported dtype: uint8, uint16, uint32, int8, int16, int32
        """
        if element_type not in self.alphabet_size_dict.keys():
            raise UnsupportedDtype()
        self.window_length = window_length
        self.buffer_length: int = buffer_length
        self.bitwise: bool = bitwise
        self.element_type = np.uint8 if bitwise else self.data_type.get(element_type)
        self.alphabet_size = self.alphabet_size_dict.get(element_type)
        self.data: np.ndarray = np.array([])  # 2d array, each column is a sample
        self.distribution: np.ndarray = np.array([])  # estimated distribution
        self.entropy: np.ndarray = np.array([])
        self.structural_elements: np.ndarray = np.array([])  # indices of elements with low entropy
        self.structural_elements_values: np.ndarray = np.array([])  # mean value of structural elements
        super().__init__(ModelType.ENTROPY)

    def update_model(self, new_data: bytes, **kwargs) -> None:
        """The method is responsible to update the model based on new observations.
        :param new_data: observation used to refine model
        :param kwargs: all other arguments which the model may require for the update
        """
        if len(new_data) != self.buffer_length:
            raise IncorrectBufferLength()
        arr = np.array([np.frombuffer(new_data, dtype=self.element_type)]).T
        if self.bitwise:
            arr = np.unpackbits(arr, axis=0)
        self.data = arr if self.data.size == 0 else np.append(self.data, arr, axis=1)
        if (self.window_length is not None) and self.data.shape[1] > self.window_length:
            # trim old messages according to window
            self.data = self.data[:, self.data.shape[1] - self.window_length:]
        self.distribution = prob(self.data)
        self.entropy = np.array(entropy(self.distribution))

    def predict(self, data: bytes, **kwargs) -> tuple[bytes, np.ndarray]:
        """Responsible for making predictions regarding originally sent data, based on recent observations and model.
        :param data: recent observation regrading which a prediction is required.
        :param kwargs: entropy_threshold kw expected as float.
        :raises: ValueError if entropy_threshold kw isn't provided
        :rtype: tuple[bytes, np.ndarray]
        """
        observation = np.array([np.frombuffer(data, dtype=self.element_type)]).T
        if self.bitwise:
            observation = np.unpackbits(observation, axis=0)
        if isinstance(kwargs.get("entropy_threshold"), (float, int)):
            self.infer_structure(kwargs.get("entropy_threshold"))
        else:
            raise ValueError()

        # replace structural bytes
        prediction = observation.copy()
        prediction[self.structural_elements] = np.array([self.structural_elements_values]).T
        if self.bitwise:
            prediction = np.round(prediction).astype(int)
            prediction = np.packbits(prediction, axis=0)
        return prediction.tobytes(), self.entropy

    def infer_structure(self, entropy_threshold: Union[float, int]) -> None:
        """structural elements are element with small enough entropy with respect to a threshold"""
        self.structural_elements = np.flatnonzero(self.entropy < entropy_threshold)
        self.structural_elements_values = np.mean(self.data[self.structural_elements], axis=1)

    def get_structure(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Getter for structure members, no calculation.
        :return: structural_elements, structural_elements_values
        """
        return self.structural_elements, self.structural_elements_values
