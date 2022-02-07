from decoders import Decoder, DecoderType
from inference import BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta
from collections.abc import Sequence
from ldpc.decoder import LogSpaDecoder
from numpy.typing import NDArray
import numpy as np
from typing import Optional
from utils.custom_exceptions import IncorrectBufferLength
from utils.information_theory import prob, entropy


class EntropyBitwiseDecoder(Decoder):
    """
    This decoder creates a model of the data, classifying them into structural and non-structural bits, based on their
    entropy across buffers.
    The decoder updates "channel" llr per model for structural bits between LDPC iterations.
    """

    def __init__(self, ldpc_decoder: LogSpaDecoder, model_length: int, entropy_threshold: float, clipping_factor: int,
                 window_length: Optional[int] = None) -> None:
        """

        :param ldpc_decoder: decoder for ldpc code used
        :param feedback_iter: number of iterations of for decoding
        :param model_length: length of assumed model in  bits
        :param entropy_threshold: threshold for entropy to dictate structural elements
        :param window_length: number of last messages to consider when evaluating distribution and entropy. If none all
        previous messages are considered.
        """
        self.segmentor: BufferSegmentation = BufferSegmentation(meta.protocol_parser)
        self.ldpc_decoder: LogSpaDecoder = ldpc_decoder
        # self.feedback_iter: int = feedback_iter
        self.model_length: int = model_length  # in bits
        self.entropy_threshold = entropy_threshold
        self.model_bits_idx = self.ldpc_decoder.info_idx  # bit indices (among codeword bits) of model bits
        self.model_bits_idx[self.model_length:] = False
        self.clipping_factor = clipping_factor  # The model llr is clipped to +-clipping_factor * max_chanel_llr
        self.window_length = window_length
        self.model_data: NDArray[np.uint8] = np.array([])  # 2d array, each column is a sample
        self.distribution: NDArray[np.float_] = np.array([])  # estimated distribution model
        self.entropy: NDArray[np.float_] = np.array([])  # estimated entropy of distribution model
        self.structural_elements: NDArray[np.int_] = np.array([])  # indices of elements with low entropy
        self.structural_elements_llr: NDArray[np.float_] = np.array([])  # value of structural elements
        super().__init__(DecoderType.ENTROPY)

    def decode_buffer(self, channel_llr: Sequence[np.float_]) -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int, int]:
        """decodes a buffer

        :param channel_llr: channel llr of bits to decode
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations, no of mavlink messages found)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - number of MAVLink messages found within buffer
        """
        estimate, llr, decode_success, iterations = self.ldpc_decoder.decode(channel_llr)
        if decode_success:
            model_bits = estimate[self.model_bits_idx]
            model_bytes: bytes = np.packbits(model_bits).tobytes()
            msg_parts, validity, structure = self.segmentor.segment_buffer(model_bytes)
            if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
                self.update_model(model_bits)
            return estimate, llr, decode_success, iterations, len(structure)

        model_llr = self.model_prediction(channel_llr)  # type: ignore
        estimate, llr, decode_success, iterations = self.ldpc_decoder.decode(model_llr)
        model_bits = estimate[self.model_bits_idx]
        model_bytes = np.packbits(model_bits).tobytes()
        msg_parts, validity, structure = self.segmentor.segment_buffer(model_bytes)
        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            self.update_model(model_bits)
        return estimate, llr, decode_success, iterations, len(structure)

    def update_model(self, bits: NDArray[np.int_]) -> None:
        """
        update model of data
        :param bits: hard estimate for bit values, assumed to be correct.
        """
        if len(bits) != self.model_length:
            raise IncorrectBufferLength()
        arr = bits[np.newaxis]
        self.model_data = arr.T if self.model_data.size == 0 else np.append(self.model_data, arr.T, axis=1)
        if (self.window_length is not None) and self.model_data.shape[1] > self.window_length:
            # trim old messages according to window
            self.model_data = self.model_data[:, self.model_data.shape[1] - self.window_length:]
        self.distribution = prob(self.model_data)
        self.entropy = entropy(self.distribution)

    def model_prediction(self, observation: NDArray[np.float_]) -> NDArray[np.float_]:
        """Responsible for making predictions regarding originally sent data, based on recent observations and model.
        :param observation: recent observation regrading which a prediction is required.
        :return: an array of llr based on model predictions
        """
        # infer structure
        self.structural_elements = np.flatnonzero(self.entropy < self.entropy_threshold)
        # model llr is calculated as log(Pr(c=0 | model) / Pr(c=1| model))
        llr = observation.copy()
        if self.model_data.size > 0 and self.model_data.shape[1] > 10:
            clipping = self.clipping_factor * max(llr)
            llr[self.structural_elements] += np.clip(
                np.log(
                    (np.finfo(np.float_).eps + self.distribution[:, 0])/(self.distribution[:, 1] + np.finfo(np.float_).eps)
                ),
                -clipping, clipping)[self.entropy < self.entropy_threshold]
        return llr


__all__ = ["EntropyBitwiseDecoder"]
