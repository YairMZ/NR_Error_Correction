"""Basic decoder"""
from decoders import Decoder, DecoderType
from inference import BufferStructure, KnownSender, BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta
from typing import Union
from protocol_meta import FrameHeader
from algo import EntropyAlgorithm
from data_models import EntropyModel
from bitstring import Bits
from collections.abc import Sequence
import numpy as np


class EntropyDecoder(Decoder):
    """base class for potential decoders"""
    def __init__(self, buffer_length: int) -> None:
        self.known_structures: list[BufferStructure] = []
        self.known_senders: dict[int, KnownSender] = {}
        self.segmentor: BufferSegmentation = BufferSegmentation(meta.protocol_parser)
        self.data_model: EntropyModel = EntropyModel(buffer_length)
        super().__init__(DecoderType.ENTROPY)
        self.algorithm = EntropyAlgorithm(self.data_model, 1)  # TODO: Change the hardcoded values

    def decode_buffer(self, channel_word: Sequence[np.float_]) -> tuple[bytes, bool]:
        """decodes a buffer

        :param channel_word: buffer to decode, input is a sequence of bit values.
        :return: returns a tuple (decoded_data, decoding_success)
        :rtype: tuple[bytes, bool]
        """
        buffer = Bits(auto=channel_word).tobytes()
        msg_parts, validity, structure = self.segmentor.segment_buffer(buffer)
        if structure:  # if messages were found register them to sender
            for idx, msg_id in structure.items():
                hdr = FrameHeader.from_buffer(buffer[idx:idx+meta.header_len])
                msg_buffer = buffer[idx:idx + hdr.length + meta.protocol_overhead]
                self.register_msg_2_sender(hdr, msg_buffer)
        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            received_structure = self.register_structure(structure, buffer)
            self.data_model.update_model(buffer)
        else:  # some bad data
            bad_parts = self.segmentor.bad_buffer_idx(buffer, msg_parts)
            if isinstance(bad_parts, list):
                buffer, entropy = self.algorithm.correct_data(buffer, *bad_parts)
                msg_parts, validity, structure = self.segmentor.segment_buffer(buffer)
                if MsgParts.UNKNOWN not in msg_parts:
                    self.data_model.update_model(buffer)
        return buffer, MsgParts.UNKNOWN not in msg_parts

    def register_structure(self, buffer_structure: Union[dict[int, int], BufferStructure], buffer: bytes
                           ) -> BufferStructure:
        """add a buffer structure to known received buffer structures."""
        if isinstance(buffer_structure, BufferStructure) and not buffer_structure.structure:
            raise ValueError("can't register an empty structure")
        if isinstance(buffer_structure, dict) and not buffer_structure:
            raise ValueError("can't register an empty structure")

        received_structure = None
        for structure in self.known_structures:
            if structure == buffer_structure:
                received_structure = structure
                break
        if received_structure is None:  # new kind of structure
            if isinstance(buffer_structure, BufferStructure):
                received_structure = buffer_structure
            else:
                received_structure = BufferStructure(buffer_structure)
            self.known_structures.append(received_structure)

        received_structure.register_buffer(buffer)

        return received_structure

    def register_msg_2_sender(self, header: FrameHeader, msg_buffer: bytes) -> None:
        """add a message to message known to be sent by sender"""
        if header.sys_id not in self.known_senders:  # if this is a new sender
            self.known_senders[header.sys_id] = KnownSender(header.sys_id)
        sender = self.known_senders.get(header.sys_id)
        if isinstance(sender, KnownSender):
            sender.register_msg(header.comp_id, header.msg_id, msg_buffer)
