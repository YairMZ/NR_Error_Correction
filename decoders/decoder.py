"""general base class for all decoders"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any
from collections.abc import Sequence


class DecoderType(Enum):
    """Enumerate models"""
    ENTROPY = auto()
    RECTIFYING = auto()


class Decoder(ABC):
    """The class serves as a base class for all data models, and server as an interface"""
    def __init__(self, decoder_type: DecoderType):
        self.decoder_type = decoder_type

    @abstractmethod
    def decode_buffer(self, channel_word: Sequence[int]) -> Any:
        """decodes a buffer

        :param channel_word: buffer to decode, input can be decimal (int) byte or bit values.
        :return: returns a tuple (decoded_data, decoding_success)
        :rtype: tuple[bytes, bool]
        """
