"""Class for implementing entropy based error correction"""
from data_models import EntropyModel
from typing import Any
from algo import CorrectionAlgorithm, AlgorithmType
from typing import Union


class EntropyAlgorithm(CorrectionAlgorithm):
    """This Algorithm assumes a known unique structure for data, although several instances can be used for
    different structures. Assuming a unique structure, entropy of bits is used model the data.
    Inferred structural bits are then forced to attempt correction.
    """
    def __init__(self, data_model: EntropyModel, entropy_threshold: Union[int, float]):
        """
        :param data_model: An EntropyModel object
        :param entropy_threshold: threshold to be used for structure inference
        """
        self.entropy_threshold = entropy_threshold
        super().__init__(AlgorithmType.ENTROPY_BASED, data_model)

    def correct_data(self, data: bytes, *args: Any, **kwargs: Any) -> tuple[bytes, Any]:
        """Attempt to correct data using the entropy model. args ere expected to be tuples of staring and ending indices
        of bad buffer parts

        :param data: recent observation
        :return: return a tuple containing a prediction as a bytes object and some confidence measure as second element.
        """
        model_prediction, entropy = self.model.predict(data, entropy_threshold=self.entropy_threshold)
        prediction = bytearray(data)
        for start_idx, end_idx in args:
            prediction[start_idx:end_idx] = model_prediction[start_idx:end_idx]
        return bytes(prediction), entropy
