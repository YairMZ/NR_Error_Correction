"""Entropy decoder"""
from decoders import Decoder, DecoderType
from inference import BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta
from data_models import EntropyModel
from collections.abc import Sequence
from ldpc.decoder import LogSpaDecoder
from numpy.typing import NDArray
import numpy as np


class EntropyBitwiseDecoderSingleStructureFlipping(Decoder):
    """
    This decoder assumes all buffers share a single structure.
    It creates a model of the data, classifying them into structural and non-structural bits, based on their entropy across
    buffers.
    Structural bits are flipped if wrong
    """
    def __init__(self, ldpc_decoder: LogSpaDecoder, exchanges: int, model_length: int, entropy_threshold: float) -> None:
        self.segmentor: BufferSegmentation = BufferSegmentation(meta.protocol_parser)
        self.ldpc_decoder: LogSpaDecoder = ldpc_decoder
        self.exchanges: int = exchanges
        self.model_length: int = model_length
        self.model: EntropyModel = EntropyModel(model_length//8)
        self.entropy_threshold = entropy_threshold
        self.model_bits_idx = self.ldpc_decoder.info_idx
        self.model_bits_idx[self.model_length:] = False
        super().__init__(DecoderType.ENTROPY)

    def decode_buffer(self, channel_word: Sequence[np.float_]) -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int, int]:
        """decodes a buffer

        :param channel_word: bits to decode
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations, no of mavlink messages found)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - number of MAVLink messages found within buffer
        """
        estimate = np.array(channel_word, dtype=np.int_)
        iterations_to_convergence = 0
        for _ in range(self.exchanges + 1):
            estimate, llr, decode_success, iterations = self.ldpc_decoder.decode(estimate)
            iterations_to_convergence += iterations
            info_bytes: bytes = self.ldpc_decoder.info_bits(estimate).tobytes()[:self.model_length//8]
            msg_parts, validity, structure = self.segmentor.segment_buffer(info_bytes)
            if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
                self.model.update_model(info_bytes)
                break
            else:  # some bad data
                model_prediction, entropy = self.model.predict(info_bytes, entropy_threshold=self.entropy_threshold)
                bitwise_prediction = np.unpackbits(np.frombuffer(model_prediction, dtype=np.uint8))
                estimate[self.model_bits_idx] = bitwise_prediction

        return estimate, llr, decode_success, iterations_to_convergence, len(structure)
