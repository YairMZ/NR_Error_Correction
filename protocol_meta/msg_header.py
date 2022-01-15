"""Handling of Mavlink headers"""
from __future__ import annotations
from protocol_meta import dialect_meta as meta
import bitstring
from utils.custom_exceptions import NonUint8
from utils.bit_operations import hamming_distance
from typing import Optional


class HeaderLength(Exception):
    """Raised when a header of incorrect length is considered"""
    pass


class NonExistentMsdId(Exception):
    """Raised when trying to consider a msg id which doesn't exist in the protocol"""
    pass


def is_valid_header(buffer: bytes) -> bool:
    """
    The function test if a buffer starts with a magic marker, and if sys_id and msg_id are consistent

    :param buffer: 6 byte buffer perhaps containing a valid MAVLink header
    """
    if len(buffer) != meta.header_len:
        return False
    # first byte must be STX (start of frame)
    # second and sixth byte are dependent on each other due to protocol limitation.
    # buffer[0] stx
    # buffer[5]  msg_id
    # buffer[1]  msg_len
    return buffer[0] == meta.stx and buffer[5] in meta.msgs_length.keys() and meta.msgs_length.get(buffer[5]) == buffer[1]


def hamming_distance_2_valid_header(buffer: bytes, max_len: Optional[int] = None) -> tuple[int, int]:
    """
    The function calculates the Hamming distance to the closest valid header. A valid header starts with magic marker,
    and has valid msg_id and corresponding length

    :param buffer: buffer containing supposed header.
    :param max_len: if the maximal length is apriori (such as for instance limited by buffer length), it can be sent to
    ignore messages too long. The length sent should be that of the payload.
    :return: a tuple of (min_dist, chosen_msg_id) where chosen_msg_id the closest msg id with respect to valid headers,
    and min_dist is the minimal Hamming distance found.
    """
    if len(buffer) != meta.header_len:
        raise HeaderLength("incorrect header length of {}".format(len(buffer)))
    dist = hamming_distance(meta.stx, buffer[0])  # distance from magic marker \xFE

    # find minimal distance from possible lengths and message ids
    min_dist = 17  # since we're comparing the Hamming distance of two byte pairs, hamming distance cannot exceed 16
    chosen_msg_id: int = -1

    for msg_id, msg_len in meta.msgs_length.items():
        candidate_dist = hamming_distance(msg_len, buffer[1]) + hamming_distance(msg_id, buffer[5])
        if candidate_dist < min_dist and (max_len is None or msg_len <= max_len):
            min_dist = candidate_dist
            chosen_msg_id = msg_id
        if candidate_dist == 0:
            break

    dist += min_dist
    return dist, chosen_msg_id


class FrameHeader:
    """A class holding a MAVLink message header"""

    def __init__(self, msg_id: int, sys_id: int, comp_id: int, seq: int):
        if sys_id < 0 or comp_id < 0 or seq < 0 or sys_id > 255 or comp_id > 255 or seq > 255:
            raise NonUint8("invalid input, msg_id: {}, comp_id: {}, seq: {}".format(msg_id, comp_id, seq))
        if msg_id in meta.msgs_length:
            length: int = meta.msgs_length.get(msg_id)  # type: ignore
        elif msg_id < 0 or msg_id > 255:
            raise NonUint8(msg_id)
        else:
            raise NonExistentMsdId("msg_id {} does not exist".format(msg_id))

        self.buffer: bytes = bytes([meta.stx, length, seq, sys_id, comp_id, msg_id])

    @property
    def length(self) -> int:
        """length of payload"""
        return self.buffer[1]

    @property
    def sequence(self) -> int:
        """seq number of packet"""
        return self.buffer[2]

    @property
    def sys_id(self) -> int:
        """sender sys id"""
        return self.buffer[3]

    @property
    def comp_id(self) -> int:
        """sender comp id"""
        return self.buffer[4]

    @property
    def msg_id(self) -> int:
        """msg if of msg"""
        return self.buffer[5]

    @property
    def bit_string(self) -> bitstring.Bits:
        """bitstring representation of buffer"""
        return bitstring.Bits(bytes=self.buffer)

    def hamming_distance(self, some_buffer: bytes) -> int:
        """Hamming distance between some_buffer and self.buffer"""
        if len(some_buffer) != meta.header_len:
            raise HeaderLength("incorrect header length of {}".format(len(some_buffer)))
        return hamming_distance(self.buffer, some_buffer)

    def __str__(self) -> str:
        return "sys_id " + str(self.sys_id) + ", msg_id " + str(self.msg_id)

    def __repr__(self) -> str:
        return str(self.buffer)

    @classmethod
    def from_buffer(cls, buffer: bytes, force_msg_id: Optional[int] = None) -> FrameHeader:
        """
        construct  aframe header from a buffer
        :param buffer: buffer of appropriate length
        :param force_msg_id: if send the value will be forced as the msg id, ignoring the buffer (for reconstruction)
        :return:
        """
        if len(buffer) != meta.header_len:
            raise HeaderLength("incorrect header length of {}".format(len(buffer)))
        seq, sys_id, comp_id, msg_id = tuple(buffer[2:])
        if force_msg_id is not None:
            msg_id = force_msg_id
        return cls(msg_id, sys_id, comp_id, seq)
