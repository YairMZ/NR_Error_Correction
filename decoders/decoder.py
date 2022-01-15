"""general base class for all decoders"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from data_models import DataModel
from typing import Optional


class DecoderType(Enum):
    """Enumerate models"""
    ENTROPY = auto()
    RECTIFYING = auto()


class Decoder(ABC):
    """The class serves as a base class for all data models, and server as an interface"""
    def __init__(self, decoder_type: DecoderType, data_model: Optional[DataModel] = None):
        self.decoder_type = decoder_type
        self.data_model = data_model

    @abstractmethod
    def decode_buffer(self, buffer: bytes) -> tuple[bytes, bool]:
        """decodes a buffer

        :param buffer: buffer to decode
        :return: returns a tuple (decoded_data, decoding_success)
        :rtype: tuple[bytes, bool]
        """
