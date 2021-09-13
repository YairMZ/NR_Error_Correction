from inference import BufferStructure, KnownSender, BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta
from typing import Union
from protocol_meta import FrameHeader


class Decoder:
    """base class for potential decoders"""
    def __init__(self):
        self.known_structures: list[BufferStructure] = []
        self.known_senders: dict[int, KnownSender] = {}
        self.segmentor: BufferSegmentation = BufferSegmentation(meta.msgs_length, meta.protocol_parser)

    def decode_buffer(self, buffer: bytes):
        """decodes a buffer"""
        msg_parts, validity, structure = self.segmentor.segment_buffer(buffer)
        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            received_structure = self.register_structure(structure, buffer)
        if structure:  # if messages were found register them to sender
            for idx, msg_id in structure.items():
                hdr = FrameHeader.from_buffer(buffer[idx:idx+meta.header_len])
                msg_buffer = buffer[idx:idx + hdr.length + meta.protocol_overhead]
                self.register_msg_2_sender(hdr, msg_buffer)

    def register_structure(self, buffer_structure: Union[dict, BufferStructure], buffer: bytes) -> BufferStructure:
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

    def register_msg_2_sender(self, header: FrameHeader, msg_buffer: bytes):
        """add a message to message known to be sent by sender"""
        if header.sys_id not in self.known_senders:  # if this is a new sender
            self.known_senders[header.sys_id] = KnownSender(header.sys_id)
        sender = self.known_senders.get(header.sys_id)
        if isinstance(sender, KnownSender):
            sender.register_msg(header.comp_id, header.msg_id, msg_buffer)
