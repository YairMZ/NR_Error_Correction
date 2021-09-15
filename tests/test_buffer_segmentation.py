"""Unit tests for BufferStructure class"""
from inference import BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta
import numpy as np

# setup test data
good_buffer = b'\xfe\x13\x00\x01\x00\xd4\x92\x01K\x16+G\xc0D+\xf4\n?\x00\x00\x80?<\t\x01\x896\xfe\n\x01\x01\x00\xda' \
              b'\x92\x01K\x16Z\x0c>\x10\x01d\xd0\xf5\xfe,\x02\x02\x00!\xd1\xffJ\x16\x12?\x97\x11\xb3"\xd2\x14\x00\x00' \
              b'\xc8B\x00\x00\xc8B\x00\x00\xc8B\xef\xfa\x10@\xbe\x1b^>\xb1\xd4\xda>\x05\x9d\xb8=D\x0b}BZ\xb9\xfe\x0c' \
              b'\x03\x01\xc8\xea\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb6r'
bad_buffer = good_buffer[:27] + bytes([1]) + good_buffer[28:]


class TestBufferSegmentation:
    def test_segment_buffer(self) -> None:
        # good buffer
        bs = BufferSegmentation(meta.protocol_parser)
        msg_parts, bit_validity, buffer_structure = bs.segment_buffer(good_buffer)
        assert MsgParts.UNKNOWN not in msg_parts
        assert buffer_structure == {0: 212, 27: 218, 45: 33, 97: 234}
        np.testing.assert_array_equal(bit_validity, np.ones(len(good_buffer)*8, dtype=int))

        # bad buffer - replace first byte in second message
        msg_parts, bit_validity, buffer_structure = bs.segment_buffer(bad_buffer)
        assert MsgParts.UNKNOWN not in msg_parts[:27]
        np.testing.assert_array_equal(msg_parts[27:45], np.array([MsgParts.UNKNOWN]*18))
        assert MsgParts.UNKNOWN not in msg_parts[45:]
        np.testing.assert_array_equal(bit_validity[:27 * 8], np.ones(27 * 8, dtype=int))
        np.testing.assert_array_equal(bit_validity[27 * 8: 45 * 8], np.zeros(18 * 8, dtype=int))
        np.testing.assert_array_equal(bit_validity[45 * 8:], np.ones(72 * 8, dtype=int))

    def test_bad_buffer_parts(self) -> None:
        bs = BufferSegmentation(meta.protocol_parser)
        msg_parts, bit_validity, buffer_structure = bs.segment_buffer(bad_buffer)
        bad_part = bs.bad_buffer_parts(bad_buffer, msg_parts)
        assert bad_part == {27: bad_buffer[27:45]}

    def test_bad_buffer_idx(self) -> None:
        bs = BufferSegmentation(meta.protocol_parser)
        msg_parts, bit_validity, buffer_structure = bs.segment_buffer(bad_buffer)
        bad_part = bs.bad_buffer_idx(bad_buffer, msg_parts)
        assert bad_part == [(27, 45)]
