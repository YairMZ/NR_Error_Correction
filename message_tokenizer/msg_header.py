import data_generation.mavlink_utils.clustering_dialect as dialect
import message_tokenizer.msg_meta as meta
import bitstring


class FrameHeader:
    def __init__(self, msg_id: int, sys_id: int, comp_id: int, seq: int):
        field_types = dialect.mavlink_map.get(msg_id).fieldtypes
        length = meta.msgs_length.get(msg_id)

        self.buffer = meta.STX + bytes([length, seq, sys_id, comp_id, msg_id])

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
        if len(some_buffer) != 6:
            raise ValueError("MAVLink has a 6 bytes header")
        # noinspection PyRedundantParentheses
        return ((self.bit_string) ^ bitstring.Bits(bytes=some_buffer)).count(True)


if __name__ == "__main__":
    hdr = FrameHeader(dialect.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 1, 1, 1)
    bits = hdr.bit_string
    print(bits)
    other_bits = bitstring.BitArray(bits)
    other_bits[0:3] = 0
    print(hdr.hamming_distance(other_bits.bytes))
