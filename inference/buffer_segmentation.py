"""break down a buffer to good and bad parts. Classify buffer parts according to protocol meta data"""
from __future__ import annotations
from enum import Enum
import bitstring  # type: ignore
from .senders import KnownSender
from protocol_meta import dialect_meta as meta
from protocol_meta import hamming_distance_2_valid_header, FrameHeader, is_valid_header, MAVError
from typing import Callable
from array import array
import numpy as np
from typing import Union
from utils.bit_operations import hamming_distance


class MsgParts(Enum):
    """various types of message parts per protocol meta"""
    HEADER = 0
    PAYLOAD = 1
    CHECKSUM = 2
    UNKNOWN = 3     # used when looking for header in corrupted data


class BufferStructure:
    """A buffer structure is characterized a set of messages which appear in hte buffer in hte same order """
    def __init__(self, msgs: dict):
        """
        :param msgs: a dict, keys are indices of start of frame within buffer, values are msg ids.
        """
        self.structure: dict = msgs
        self.reception_count: int = 0
        self.received_buffers: list[bytes] = []

    def __eq__(self, other) -> bool:
        """We define equality of the structure itself, irrespective of self.received_buffers"""
        if isinstance(other, BufferStructure):
            return self.structure == other.structure
        if isinstance(other, dict):
            return self.structure == other
        return False

    def register_buffer(self, buffer: bytes) -> None:
        """
        add a received buffer to list of buffers

        :param buffer: whole buffer containing also payload
        """
        if self.adheres_to_structure(buffer):
            self.received_buffers.append(buffer)
            self.reception_count += 1
        else:
            raise ValueError()

    def __str__(self) -> str:
        return str(self.structure)

    def __len__(self):
        """returns the number of messages in structures"""
        return len(self.structure)

    def adheres_to_structure(self, buffer: bytes) -> bool:
        """Test if a buffer adheres to a structure

        :param buffer: candidate buffer
        """
        for idx, msg_id in self.structure.items():
            hdr = FrameHeader.from_buffer(buffer[idx:idx + meta.header_len])
            if hdr.msg_id != msg_id:
                return False
        return True


class BufferSegmentation:
    """The class aims to break down a buffer to an ML sequence of MAVLink messages."""
    def __init__(self, protocol_parser_handler: Callable):
        """
        :param protocol_parser_handler: handler function to parse buffer according to protocol. Handler should return
        data, and if successful
        """
        self.protocol_parser = protocol_parser_handler

    def segment_buffer(self, buffer: bytes) -> tuple[np.ndarray, np.ndarray, dict]:
        """
        Breaks down a buffer to several MAVLink messages. Doesn't attempt any
        reconstruction, only break down to good and bad parts.

        :param buffer: a buffer containing one or more MAVLink msgs
        :return: a tuple. The first element is a np.ndarray of predicted message parts. The second is an np.ndarray of
        bit validity. The third is a BufferStructure object.
        """

        msg_parts = np.array([MsgParts.UNKNOWN]*len(buffer))  # Holds an enum value per bytes of the message.
        # It tells how was it classified
        bit_validity = np.array([0]*len(buffer) * 8)  # This tells how certain are we of the correctness of bit value.
        # 1 is correct, -1 is incorrect, and 0 is unknown
        buffer_structure = {}

        # Go over buffer once. Locate good messages, passing CRC
        for byte_idx in range(len(buffer) - meta.protocol_overhead + 1):  # don't go over last bytes as to not raise a
            # an exception. No message can be there anyway
            if msg_parts[byte_idx] != MsgParts.UNKNOWN:
                continue
            if is_valid_header(buffer[byte_idx:byte_idx+meta.header_len]):
                # Construct a header
                header = FrameHeader.from_buffer(buffer[byte_idx:byte_idx+meta.header_len])
                candidate_buffer = array("B", buffer[byte_idx:byte_idx + header.length + meta.protocol_overhead])
                try:
                    self.protocol_parser(candidate_buffer)  # simply see if exception is raised or not

                    # if decode is successful buffer parts are known and bits are valid
                    msg_parts[byte_idx:byte_idx+meta.header_len] = MsgParts.HEADER
                    msg_parts[byte_idx + meta.header_len:byte_idx + meta.header_len + header.length] = \
                        MsgParts.PAYLOAD
                    msg_parts[byte_idx + meta.header_len + header.length:
                              byte_idx + meta.protocol_overhead + header.length] = MsgParts.CHECKSUM
                    bit_validity[byte_idx*8: (byte_idx+len(candidate_buffer))*8] = 1

                    # register structure
                    buffer_structure[byte_idx] = header.msg_id
                except MAVError as e:
                    print(e)
                    print(candidate_buffer)

        return msg_parts, bit_validity, buffer_structure

    @staticmethod
    def bad_buffer_parts(buffer: bytes, msg_parts: np.ndarray) -> dict:
        """The function returns sub buffers of bad parts

        :param buffer: a buffer containing one or more MAVLink msgs
        :param msg_parts: an np.ndarray which holds an enum value per bytes of the message, which tells how was it
        classified.
        :return: a dict with keys as byte index in original buffer and values of bad sub buffers
        """
        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            return {}

        # locate bad parts of buffer, break down to sub buffers
        bad_buffer_parts: dict[int, bytes] = {}
        length = 0
        byte_idx = 0
        while byte_idx < len(buffer):
            if msg_parts[byte_idx] == MsgParts.UNKNOWN:
                length += 1
            else:
                if length > 0:  # previous byte was the last bad byte in a buffer part
                    bad_buffer_parts[byte_idx - length] = buffer[byte_idx - length:byte_idx]
                length = 0
            byte_idx += 1
        if length > 0:  # last part was bad
            bad_buffer_parts[byte_idx - length] = buffer[byte_idx - length:byte_idx]
        return bad_buffer_parts
