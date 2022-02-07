"""Rectifying decoder"""
from decoders import Decoder, DecoderType
from collections.abc import Sequence
from ldpc.decoder import LogSpaDecoder, bsc_llr
import numpy as np
from inference import BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta
from numpy.typing import NDArray


class RectifyingDecoderSingleSegmentation(Decoder):
    """
    This decoder assumes all buffers must contain at least one full MAVLink message.
    Thus, it breaks down buffers to "good" and "bad" parts. It then updates the channel model per part.
    Since a buffer may contain padding at the end which cannot be interpreted as messages even without errors, it is best not
    to assume too high bit flip probability even for "bad parts".

    The decoder performs a single classification before ldpc decoder
    """
    def __init__(self, ldpc_decoder: LogSpaDecoder, k: int,
                 default_p: float, bad_p: float, good_p: float = 1e-7) -> None:

        self.ldpc_decoder = ldpc_decoder
        self.bs = BufferSegmentation(meta.protocol_parser)
        self.k = k
        self.bad_p = bad_p
        self.good_p = bsc_llr(p=good_p)
        self.default_p = bsc_llr(p=default_p)
        self.info_bits_node_uids = [node.uid for node in self.ldpc_decoder.ordered_vnodes()][:self.k]
        super().__init__(DecoderType.RECTIFYING)

    def decode_buffer(self, channel_word: Sequence[int]) -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int, int]:
        """decodes a buffer

        :param channel_word: bits to decode
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations, no of mavlink messages found)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - number of MAVLink messages found within buffer
        """
        # initialize decoder channel models
        self.ldpc_decoder.update_channel_model({node: self.default_p for node in self.info_bits_node_uids})
        info_bytes = self.ldpc_decoder.info_bits(np.array(channel_word, dtype=np.int_)).tobytes()
        # look for good parts
        parts, validity, structure = self.bs.segment_buffer(info_bytes)

        # rectify channel models
        good_bits = np.repeat(parts != MsgParts.UNKNOWN, 8)
        bad_bits = np.repeat(parts != MsgParts.UNKNOWN, 8)[:self.k]
        bad_p = bsc_llr(p=self.bad_p)
        # bad_p = bsc_llr(p=self.bad_p * self.k / (8 * sum(parts == MsgParts.UNKNOWN)))
        d = {pair[0]: self.good_p if pair[1] else bad_p for pair in zip(self.info_bits_node_uids, good_bits)}
        self.ldpc_decoder.update_channel_model(d)

        # decode
        estimate, llr, decode_success, iterations = self.ldpc_decoder.decode(channel_word)
        info_bytes = self.ldpc_decoder.info_bits(np.array(estimate)).tobytes()
        parts, validity, structure = self.bs.segment_buffer(info_bytes)

        return estimate, llr, decode_success, iterations, len(structure)
