from __future__ import annotations
from enum import Enum
from senders import KnownSender
from protocol_meta import dialect_meta as meta
from protocol_meta import hamming_distance_2_valid_header, FrameHeader, is_valid_header,MAVError
from typing import Callable
from array import array
import numpy as np
from typing import Union


class MsgParts(Enum):
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
        self.structure = msgs
        self.reception_count = 0
        self.received_buffers: list[bytes] = []

    def __eq__(self, other):
        if isinstance(other, BufferStructure):
            return self.structure == other.structure
        if isinstance(other, dict):
            return self.structure == other
        return False

    def register_buffer(self, buffer: bytes):
        self.received_buffers.append(buffer)
        self.reception_count += 1

    def __str__(self):
        return str(self.structure)


class BufferSegmentation:
    """The class aims to break down a buffer to an ML sequence of MAVLink messages."""
    def __init__(self, msgs_len: dict, protocol_parser_handler: Callable):
        # noinspection LongLine
        """
        :param protocol_parser_handler: handler function to parse buffer according to protocol. Handler should return data, and if successful
        :param msgs_len: a dictionary with msg_id as keys as messages length as values
        """
        self.msgs_len = msgs_len
        self.known_structures: list[BufferStructure] = []
        self.known_senders: dict[int, KnownSender] = {}
        self.protocol_parser = protocol_parser_handler

    def parse_buffer(self, buffer: bytes) -> tuple:
        # noinspection LongLine
        """
        Break down a buffer to several MAVLink messages. Don't attempt ant reconstruction yet.


        :param buffer: a buffer containing one or more MAVLink msgs
        :return: a tuple. The first element is a np.array of predicted message parts. The second is an np array of bit validity. The third is a dict with keys as indices of start of frame within buffer, values predicted msg ids.
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
                    if header.sys_id not in self.known_senders:
                        self.known_senders[header.sys_id] = KnownSender(header.sys_id)
                    self.known_senders.get(header.sys_id).register_msg(
                        header.comp_id, header.msg_id, buffer[byte_idx:byte_idx+header.length+meta.protocol_overhead])

                    # register structure
                    buffer_structure[byte_idx] = header.msg_id
                except MAVError as e:
                    print(e)
                    print(candidate_buffer)
                # except Exception as e:
                #     print(e)
                #     print(candidate_buffer)

        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            received_structure = self.register_structure(buffer_structure)
            return msg_parts, bit_validity, received_structure.structure
        else:  # buffer contains errors
            received_structure = BufferStructure(buffer_structure)
            received_structure.register_buffer(buffer)
            return msg_parts, bit_validity, received_structure.structure

    def reconstruct_buffer(self, buffer: bytes, max_flips: int, bit_validity: np.array = None,
                           msg_parts: np.array = None, structure: Union[dict, BufferStructure] = None):
        """

        :param buffer: a buffer containing one or more MAVLink msgs
        :param max_flips: maximal number of bit flips allowed per header to count as a valid header
        :param bit_validity: an np.array with single value per bit. This tells how certain are we of the correctness of
        bit value. 1 is correct, -1 is incorrect, and 0 is unknown. Defaults to None if unknown.
        :param msg_parts: an np.array which holds an enum value per bytes of the message, which tells how was it
        classified. Defaults to None if unknown.
        :param structure: buffer structure if known, else defaults to None
        :return:
        """
        if MsgParts.UNKNOWN not in msg_parts:  # buffer fully recovered
            received_structure = self.register_structure(structure)
            return msg_parts, bit_validity, received_structure.structure

        for bit_flips in range(max_flips + 1):
            for byte_idx in range(len(buffer) - meta.header_len + 1):
                # look for valid headers with specified bit flips
                if msg_parts[byte_idx] != MsgParts.UNKNOWN:
                    continue
                min_dist, chosen_msg_id = hamming_distance_2_valid_header(buffer[byte_idx:byte_idx + meta.header_len])

    def register_structure(self, buffer_structure: Union[dict, BufferStructure]) -> BufferStructure:
        if buffer_structure is None:
            raise ValueError("can't register an unknown structure")

        received_structure = None
        for structure in self.known_structures:
            if structure == buffer_structure:
                structure.register_buffer(buffer)
                received_structure = structure
                break
        if received_structure is None:  # new type of structure
            if isinstance(buffer_structure, BufferStructure):
                received_structure = buffer_structure
            else:
                received_structure = BufferStructure(buffer_structure)
            received_structure.register_buffer(buffer)
            self.known_structures.append(received_structure)
        return received_structure


if __name__ == "__main__":
    import pickle
    import data_generation.mavlink_utils.clustering_dialect as dialect
    with open('../data/June_20_Rafael/hc_to_ship.pickle', 'rb') as f:
        ship_rx = pickle.load(f)

    good_transmissions = [buffer for is_success, buffer in zip(ship_rx["rx_success"], ship_rx["encoded_rx"])
                          if is_success == 1]
    good_transmissions = [bytes(tx) for tx in good_transmissions]

    bad_transmissions = [buffer for is_success, buffer in zip(ship_rx["rx_success"], ship_rx["encoded_rx"])
                         if is_success == 0]
    bad_transmissions = [bytes(tx) for tx in bad_transmissions]

    all_transmissions = [bytes(tx) for tx in ship_rx["encoded_rx"]]

    mav_obj = dialect.MAVLink(1)

    bad_buffer = bytes([int(b) for b in ship_rx["encoded_rx"][3]])
    # test_buffer = array('B', good_transmissions[0][:27])
    # msg = mav_obj.decode(test_buffer)
    # msg = mav_obj.parse_buffer(good_transmissions[0])
    bs = BufferSegmentation(meta.msgs_length, mav_obj.decode)
    for buffer in good_transmissions:
        parts, validity, structure_ = bs.parse_buffer(buffer)

    interesting_buffers = []
    for idx, buffer in enumerate(bad_transmissions):
        parts, validity, structure_ = bs.parse_buffer(buffer)
        if MsgParts.HEADER in parts and MsgParts.UNKNOWN in parts:  # if found at least one good message
            interesting_buffers.append(idx)
            print(len(structure_), " good messages")
            pass
        bs.reconstruct_buffer(buffer, 2, validity, parts, structure_)
    print(len(interesting_buffers), " bad buffers with some good messages")
