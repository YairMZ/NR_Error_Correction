from .protocol_meta import dialect
from .protocol import dialect_meta as meta
import bitstring


def is_valid_header(buffer: bytes) -> bool:
    """
    The function test if a buffer starts with a magic marker, and if sys_id and msg_id are consistent

    :param buffer: 6 byte buffer perhaps containing a valid MAVLink header
    """
    if len(buffer) != meta.header_len:
        return False
    # first byte must be STX (start of frame)
    # second and sixth byte are dependent on each other due to protocol limitation.
    t1 = buffer[0]
    t2 = buffer[5]
    t3 = buffer[1]
    t4 = meta.msgs_length
    return buffer[0] == meta.stx and buffer[5] in meta.msgs_length.keys() and \
           meta.msgs_length.get(buffer[5]) == buffer[1]


def hamming_distance_2_valid_header(buffer: bytes) -> tuple:
    """
    The function calculates the Hamming distance to the closest valid header.
    :param buffer:
    :return: a tuple of min_dist, chosen_msg_id if the buffer is of correct length, otherwise None. None
    """
    if len(buffer) != meta.header_len:
        return None, None
    dist = bitstring.Bits(uint=254 ^ buffer[0], length=8).count(True)  # distance from magic marker \xFE

    # find minimal distance from possible lengths and message ids
    min_dist = 17  # since we're comparing the Hamming distance of two byte pairs, hamming distance cannot exceed 16
    chosen_msg_id = None

    for msg_id, msg_len in meta.msgs_length.items():
        candidate_dist = bitstring.Bits(uint=msg_len ^ buffer[1], length=8).count(True) + \
                         bitstring.Bits(uint=msg_id ^ buffer[5], length=8).count(True)
        if candidate_dist < min_dist:
            min_dist = candidate_dist
            chosen_msg_id = msg_id
        if candidate_dist == 0:
            break

    dist += min_dist
    return min_dist, chosen_msg_id


class FrameHeader:
    """A class holding a MAVLink message header"""

    def __init__(self, msg_id: int, sys_id: int, comp_id: int, seq: int):
        try:
            field_types = dialect.mavlink_map.get(msg_id).fieldtypes
        except AttributeError:
            raise ValueError("msg_id {} does not exist".format(msg_id))
        length = meta.msgs_length.get(msg_id)

        self.buffer = bytes([meta.stx, length, seq, sys_id, comp_id, msg_id])

    @property
    def length(self) -> int:
        return self.buffer[1]

    @property
    def sequence(self) -> int:
        return self.buffer[2]

    @property
    def sys_id(self) -> int:
        return self.buffer[3]

    @property
    def comp_id(self) -> int:
        return self.buffer[4]

    @property
    def msg_id(self) -> int:
        return self.buffer[5]

    @property
    def bit_string(self) -> bitstring.Bits:
        return bitstring.Bits(bytes=self.buffer)

    def hamming_distance(self, some_buffer: bytes) -> int:
        if len(some_buffer) != meta.header_length:
            raise ValueError("incorrect header length of {}".format(len(some_buffer)))
        # noinspection PyRedundantParentheses
        return ((self.bit_string) ^ bitstring.Bits(bytes=some_buffer)).count(True)

    def __str__(self):
        "sys_id " + str(self.sys_id) + ", msg_id " + str(self.msg_id)

    def __repr__(self):
        return str(self.buffer)

    @classmethod
    def from_buffer(cls, buffer: bytes):
        if len(buffer) != meta.header_len:
            raise ValueError("incorrect header length of {}".format(len(buffer)))
        seq, sys_id, comp_id, msg_id = tuple(b for b in buffer[2:])
        return cls(msg_id, sys_id, comp_id, seq)


if __name__ == "__main__":
    hdr = FrameHeader(dialect.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 1, 1, 1)
    bits = hdr.bit_string
    print(bits)
    other_bits = bitstring.BitArray(bits)
    other_bits[0:3] = 0
    print(hdr.hamming_distance(other_bits.bytes))
    test = FrameHeader.from_buffer(bytes([i for i in range(5)])+b"\x21")
