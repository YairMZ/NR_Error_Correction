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
    Thus, it breaks down buffers to "good" and "bad" parts. It then updates the llr per part.
    Since a buffer may contain padding at the end which cannot be interpreted as messages even without errors, it is best not
    to assume too high bit flip probability even for "bad parts"


    """
    def __init__(self, ldpc_decoder: LogSpaDecoder, segmentation_iterations: int, ldpc_iterations: int, k: int,
                 default_p: float, bad_p: float, good_p: float) -> None:
        """
        :param ldpc_decoder: decoder object for BP decoding
        :param segmentation_iterations: number of times segmentation is done.
        :param ldpc_iterations: iterations between segmentations
        :param k: number of information bearing bits
        :param default_p:
        :param bad_p:
        :param good_p:
        """

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

    def decode_buffer(self, channel_llr: Sequence[np.float_]) -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int, int]:
        """decodes a buffer

        :param channel_llr: bits to decode
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations, no of mavlink messages found)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - number of MAVLink messages found within buffer
        """
        channel_llr = np.array(channel_llr, dtype=np.float_)
        # llr_max = max(llr)
        decode_success = False
        iterations_to_convergence = 0
        for idx in range(self.segmentation_iterations + 1):
            estimate, llr, decode_success, iterations = self.ldpc_decoder.decode(channel_llr, self.ldpc_iterations)
            iterations_to_convergence += iterations
            info_bytes = self.ldpc_decoder.info_bits(estimate).tobytes()
            parts, validity, structure = self.bs.segment_buffer(info_bytes[:self.k])
            if decode_success:
                break
            good_bits = np.flatnonzero(np.repeat(parts != MsgParts.UNKNOWN, 8))
            if good_bits.size > 0 and idx < self.segmentation_iterations:
                bad_bits = np.flatnonzero(np.repeat(parts == MsgParts.UNKNOWN, 8))
                bad_p = bsc_llr(p=self.bad_p*self.k/bad_bits.size)
                rect = np.array(channel_llr < 0, dtype=np.float_)
                rect[good_bits] = self.good_p(rect[good_bits])
                rect[bad_bits] = bad_p(rect[bad_bits])
                rect[self.k:] = self.default_p(rect[self.k:])
                channel_llr = rect

        return estimate, llr, decode_success, iterations_to_convergence, len(structure)
