"""Rectifying decoder"""
from decoders import Decoder, DecoderType
from collections.abc import Sequence
from ldpc.decoder import LogSpaDecoder, bsc_llr
import numpy as np
from inference import BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta
from numpy.typing import NDArray


class RectifyingDecoder(Decoder):
    """
    This decoder assumes all buffers must contain at least one full MAVLink message.
    Thus, it breaks down buffers to "good" and "bad" parts. It then updates the channel model per part.
    Since a buffer may contain padding at the end which cannot be interpreted as messages even without errors, it is best not
    to assume too high bit flip probability even for "bad parts"
    """
    def __init__(self, ldpc_decoder: LogSpaDecoder, segmentation_iterations: int, ldpc_iterations: int, k: int,
                 default_p: float, bad_p: float, good_p: float = 1e-7) -> None:

        self.ldpc_decoder = ldpc_decoder
        self.bs = BufferSegmentation(meta.protocol_parser)
        self.segmentation_iterations = segmentation_iterations
        self.ldpc_iterations = ldpc_iterations
        self.k = k
        self.bad_p = bad_p
        self.good_p = bsc_llr(p=good_p)
        self.default_p = bsc_llr(p=default_p)
        self.v_node_uids = [node.uid for node in self.ldpc_decoder.ordered_vnodes()][:self.k]
        super().__init__(DecoderType.RECTIFYING)

    def decode_buffer(self, channel_word: Sequence[int]) -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int]:
        """decodes a buffer

        :param channel_word: bits to decode
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - number of MAVLink messages found within buffer
        """
        found = 0
        self.ldpc_decoder.update_channel_model({node: self.default_p for node in self.v_node_uids})
        ldpc_iter = self.ldpc_iterations
        estimate = np.array(channel_word, dtype=np.int_)
        decode_success = False
        for _ in range(self.segmentation_iterations + 1):
            estimate, llr, decode_success, ldpc_iteration = self.ldpc_decoder.decode(estimate, ldpc_iter)
            info_bytes = self.ldpc_decoder.info_bits(np.array(estimate)).tobytes()
            parts, validity, structure = self.bs.segment_buffer(info_bytes)
            if decode_success:
                break
            # if found >= len(structure):  # if we can't identify new parts no point to continue
            #     break
            found = len(structure)
            # ldpc_iter = 5
            good_bits = np.repeat(parts != MsgParts.UNKNOWN, 8)
            bad_p = bsc_llr(p=self.bad_p*self.k/(8*sum(parts == MsgParts.UNKNOWN)))
            d = {pair[0]: self.good_p if pair[1] else bad_p for pair in zip(self.v_node_uids, good_bits)}
            self.ldpc_decoder.update_channel_model(d)

        # if not decode_success:
        #     estimate, llr, decode_success, ldpc_iteration = self.ldpc_decoder.decode(channel_word, self.ldpc_iterations)
        #     info_bytes = self.ldpc_decoder.info_bits(np.array(estimate)).tobytes()
        #     parts, validity, structure = self.bs.segment_buffer(info_bytes)

        return estimate, llr, decode_success, len(structure)
