"""break down a buffer to good and bad parts. Classify buffer parts according to protocol metadata"""
from __future__ import annotations
from enum import Enum
from protocol_meta import dialect_meta as meta
from protocol_meta import FrameHeader, is_valid_header, MAVError
from typing import Callable, Union, Any
from array import array
import numpy as np
import numpy.typing as npt
from collections.abc import MutableSequence


class MsgParts(Enum):
    """various types of message parts per protocol meta"""
    HEADER = 0
    PAYLOAD = 1
    CHECKSUM = 2
    UNKNOWN = 3     # used when looking for header in corrupted data


class BufferStructure:
    """A buffer structure is characterized a set of messages which appear in hte buffer in hte same order """
    def __init__(self, msgs: dict[int, int]):
        """
        :param msgs: a dict, keys are indices of start of frame within buffer, values are msg ids.
        """
        self.structure: dict[int, int] = msgs
        self.reception_count: int = 0
        self.received_buffers: list[bytes] = []

    def __eq__(self, other: Any) -> bool:
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

    def __len__(self) -> int:
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
    def __init__(self, protocol_parser_handler: Callable[[MutableSequence[int]], object]):
        """
        :param protocol_parser_handler: handler function to parse buffer according to protocol. Handler should return
        data, and if successful
        """
        self.protocol_parser = protocol_parser_handler

    def segment_buffer(self, buffer: bytes) -> tuple[npt.NDArray[np.object_], npt.NDArray[np.float_], dict[int, int]]:
        """
        Breaks down a buffer to several MAVLink messages. Doesn't attempt any
        reconstruction, only break down to good and bad parts.

        :param buffer: a buffer containing one or more MAVLink msgs
        :return: a tuple. The first element is a np.ndarray of predicted message parts. The second is a np.ndarray of
        bit validity. The third is a BufferStructure object.
        """

        msg_parts: npt.NDArray[np.object_] = np.array([MsgParts.UNKNOWN]*len(buffer))  # enum value per bytes of the buffer.
        # It tells how was it classified
        bit_validity: npt.NDArray[np.float_] = np.array([0]*len(buffer) * 8, dtype=np.float_)  # certainty of bit values.
        # 1 is correct, -1 is incorrect, and 0 is unknown
        buffer_structure: dict[int, int] = {}

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
                    pass
                    # print(e)
                    # print(candidate_buffer)

        return msg_parts, bit_validity, buffer_structure

    @staticmethod
    def bad_buffer_parts(buffer: bytes, msg_parts: npt.NDArray[np.object_]) -> dict[int, bytes]:
        """The function returns sub buffers of bad parts

        :param buffer: a buffer containing one or more MAVLink msgs
        :param msg_parts: a np.ndarray which holds an enum value per bytes of the message, which tells how was it
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

    @staticmethod
    def bad_buffer_idx(buffer: bytes, msg_parts: npt.NDArray[np.object_]) -> Union[None, list[tuple[int, int]]]:
        """The function returns sub buffers of bad parts

        :param buffer: a buffer containing one or more MAVLink msgs
        :param msg_parts: a np.ndarray which holds an enum value per bytes of the message, which tells how was it
        classified.
        :return: a list of tuples, each tuple has a starting and ending index of a bad buffer part, and none if buffer
        is good
        """
        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            return None

        bad_buffer_parts: list[tuple[int, int]] = []
        length = 0
        byte_idx = 0
        while byte_idx < len(buffer):
            if msg_parts[byte_idx] == MsgParts.UNKNOWN:
                length += 1
            else:
                if length > 0:  # previous byte was the last bad byte in a buffer part
                    bad_buffer_parts.append((byte_idx - length, byte_idx))
                length = 0
            byte_idx += 1
        if length > 0:  # last part was bad
            bad_buffer_parts.append((byte_idx - length, byte_idx))
        return bad_buffer_parts
