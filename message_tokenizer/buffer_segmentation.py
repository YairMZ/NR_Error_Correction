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

valid_headers = 0
class MsgParts(Enum):
    """various types of message parts per protocol meta"""
    HEADER = 0
    PAYLOAD = 1
    CHECKSUM = 2
    UNKNOWN = 3     # used when looking for header in corrupted data


class BufferStructure:
    """For each known sequence of messages per structure"""
    def __init__(self, msgs: dict):
        """
        :param msgs: a dict, keys are indices of start of frame within buffer, values are msg ids.
        """
        self.structure: dict = msgs
        self.reception_count: int = 0
        self.received_buffers: list[bytes] = []

    def __eq__(self, other) -> bool:
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
        self.received_buffers.append(buffer)
        self.reception_count += 1

    def __str__(self) -> str:
        return str(self.structure)

    def __len__(self):
        """returns the number of messages in structures"""
        return len(self.structure)


class BufferSegmentation:
    """The class aims to break down a buffer to an ML sequence of MAVLink messages."""
    def __init__(self, msgs_len: dict, protocol_parser_handler: Callable):
        """
        :param protocol_parser_handler: handler function to parse buffer according to protocol. Handler should return
        data, and if successful
        :param msgs_len: a dictionary with msg_id as keys as messages length as values
        """
        self.msgs_len = msgs_len
        self.known_structures: list[BufferStructure] = []
        self.known_senders: dict[int, KnownSender] = {}
        self.protocol_parser = protocol_parser_handler

    def parse_buffer(self, buffer: bytes) -> tuple:
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

                    # register sender and message
                    self.register_msg_2_sender(header, bytes(candidate_buffer))

                    # register structure
                    buffer_structure[byte_idx] = header.msg_id
                except MAVError as e:
                    print(e)
                    print(candidate_buffer)
                # except Exception as e:
                #     print(e)
                #     print(candidate_buffer)

        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            received_structure = self.register_structure(buffer_structure, buffer)
        else:  # buffer contains errors
            received_structure = BufferStructure(buffer_structure)
            received_structure.register_buffer(buffer)
        return msg_parts, bit_validity, received_structure

    def register_msg_2_sender(self, header: FrameHeader, msg_buffer: bytes):
        """add a message to message known to be sent by sender"""
        if header.sys_id not in self.known_senders:  # if this is a new sender
            self.known_senders[header.sys_id] = KnownSender(header.sys_id)
        sender = self.known_senders.get(header.sys_id)
        if isinstance(sender, KnownSender):
            sender.register_msg(header.comp_id, header.msg_id, msg_buffer)

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

    def reconstruct_buffer(self, buffer: bytes, max_flips: int, bit_validity: np.ndarray, msg_parts: np.ndarray,
                           structure: Union[dict, BufferStructure] = None):
        """

        :param buffer: a buffer containing one or more MAVLink msgs
        :param max_flips: maximal number of bit flips allowed per header to count as a valid header
        :param bit_validity: an np.ndarray with single value per bit. This tells how certain are we of the correctness
        of bit value. 1 is correct, -1 is incorrect, and 0 is unknown
        :param msg_parts: an np.ndarray which holds an enum value per bytes of the message, which tells how was it
        classified.
        :param structure: buffer structure if known, else defaults to None
        :return:
        """
        global valid_headers
        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            if isinstance(structure, (dict, BufferStructure)):
                received_structure = self.register_structure(structure, buffer)
            else:
                raise ValueError("No structure given for a fully parsed buffer")
            return msg_parts, bit_validity, received_structure.structure

        # locate bad parts of buffer, break down to sub buffers
        bad_buffer_parts: list[dict[int, int]] = []
        for byte_idx in range(len(buffer)):
            if msg_parts[byte_idx] == MsgParts.UNKNOWN:
                if not bad_buffer_parts:  # first bad byte case
                    bad_buffer_parts = [{byte_idx: buffer[byte_idx]}]
                elif msg_parts[byte_idx-1] == MsgParts.UNKNOWN:  # was the previous byte also bad?
                    bad_buffer_parts[-1][byte_idx] = buffer[byte_idx]
                else:  # new bad sector
                    bad_buffer_parts.append({byte_idx: buffer[byte_idx]})

        for sub_buffer in bad_buffer_parts:
            bad_buffer = bytes(sub_buffer.values())
            for byte_idx in range(len(bad_buffer) - meta.header_len + 1):
                # look for valid headers with specified bit flips
                min_dist, chosen_msg_id = hamming_distance_2_valid_header(
                    bad_buffer[byte_idx:byte_idx + meta.header_len],
                    max_len=len(bad_buffer) - meta.protocol_overhead - byte_idx)
                if min_dist <= max_flips:  # found candidate header
                    allowed_flips = max_flips - min_dist
                    # there's a bug somewhere in code below
                    candidate_hdr = FrameHeader.from_buffer(bad_buffer[byte_idx:byte_idx + meta.header_len],
                                                            force_msg_id=chosen_msg_id)
                    if min_dist == 0:
                        valid_headers += 1
                    if min_dist > 0:
                        print("corrected {} error bits in header".format(min_dist))
                        print("original header: ", bad_buffer[byte_idx:byte_idx + meta.header_len])
                        print("corrected header: ", candidate_hdr.buffer)
                        a = bitstring.Bits(auto=bad_buffer[byte_idx:byte_idx + meta.header_len])
                        b = bitstring.Bits(auto=candidate_hdr.buffer)
                        print(hamming_distance(a, b))
                        if min_dist != hamming_distance(a, b):
                            pass
        return min_dist
