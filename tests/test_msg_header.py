"""unit tests for the msg_hdr module from the protocol meta package"""
import pytest
from protocol_meta.protocol_meta import dialect_meta as meta
from protocol_meta.msg_header import hamming_distance_2_valid_header, FrameHeader, is_valid_header, HeaderLength, \
    NonExistentMsdId
from utils.custom_exceptions import NonUint8
from utils.bit_operations import hamming_distance
from data_generation.random_test_data_generation import rand_msg, rand_uint8
import bitstring


class TestFrameHeader:
    def test_wrong_msg_id(self) -> None:

        # negative msg_id
        with pytest.raises(NonUint8):
            FrameHeader(-1, rand_uint8(), rand_uint8(), rand_uint8())
        # large msg_id
        with pytest.raises(NonUint8):
            FrameHeader(256, rand_uint8(), rand_uint8(), rand_uint8())
        possible_ids = list(range(256))
        for msg_id in meta.msg_ids:
            possible_ids.remove(msg_id)
        # non existent msg_id
        if possible_ids:  # if there are illegal ids in dialect at all test them
            with pytest.raises(NonExistentMsdId):
                FrameHeader(possible_ids[0], rand_uint8(), rand_uint8(), rand_uint8())

    def test_wrong_sys_id(self) -> None:
        # negative sys_id
        with pytest.raises(NonUint8):
            FrameHeader(rand_msg(), -1, rand_uint8(), rand_uint8())
        # large sys_id
        with pytest.raises(NonUint8):
            FrameHeader(rand_msg(), 256, rand_uint8(), rand_uint8())

    def test_wrong_comp_id(self) -> None:
        # negative comp_id
        with pytest.raises(NonUint8):
            FrameHeader(rand_msg(), rand_uint8(), -1, rand_uint8())
        # large comp_id
        with pytest.raises(NonUint8):
            FrameHeader(rand_msg(), rand_uint8(), 256, rand_uint8())

    def test_wrong_seq(self) -> None:
        # negative seq
        with pytest.raises(NonUint8):
            FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), -1)
        # large seq"):
        with pytest.raises(NonUint8):
            FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), 256)

    def test_hamming(self) -> None:
        mask = 1
        for i in range(6):
            frame = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8())
            buffer = frame.buffer
            altered_buffer = buffer[:i] + bytes([buffer[i] ^ mask]) + buffer[i+1:]
            dist = frame.hamming_distance(altered_buffer)
            assert dist == i+1
            mask = (mask << 1) + 1

    def test_hamming_wrong_length(self) -> None:
        frame = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8())
        buffer = frame.buffer
        pytest.raises(HeaderLength, frame.hamming_distance, buffer+b"1")

    def test_length(self) -> None:
        frame = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8())
        assert frame.length == meta.msgs_length[frame.msg_id]

    def test_bitstring(self) -> None:
        frame = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8())
        buffer = frame.buffer
        assert frame.bit_string == bitstring.Bits(bytes=buffer)

    def test_repr(self) -> None:
        frame = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8())
        buffer = frame.buffer
        assert repr(frame) == str(buffer)

    def test_class_method(self) -> None:
        frame = FrameHeader(meta.msg_ids[0], rand_uint8(), rand_uint8(), rand_uint8())
        buffer = frame.buffer
        assert FrameHeader.from_buffer(buffer).buffer == buffer
        with pytest.raises(HeaderLength):
            FrameHeader.from_buffer(buffer[:2])
        assert FrameHeader.from_buffer(buffer, force_msg_id=meta.msg_ids[1]).msg_id == meta.msg_ids[1]


class TestIsValidHeader:
    def test_wrong_stx(self) -> None:
        buffer = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8()).buffer
        buffer = bytes([buffer[0] >> 1]) + buffer[1:]
        val = is_valid_header(buffer)
        assert val is False

    def test_non_existent_msg_id(self) -> None:
        possible_ids = list(range(256))
        for msg_id in meta.msg_ids:
            possible_ids.remove(msg_id)
        if possible_ids:  # if there are illegal ids in dialect at all test them
            buffer = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8()).buffer
            buffer = buffer[:5] + bytes([possible_ids[0]])
            val = is_valid_header(buffer)
            assert val is False

    def test_wrong_msg_length(self) -> None:
        buffer = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8()).buffer
        buffer = bytes([buffer[0]]) + bytes([buffer[1] << 1]) + buffer[2:]
        val = is_valid_header(buffer)
        assert val is False

    def test_wrong_buffer_length(self) -> None:
        short_buffer = bytes(range(3))
        assert is_valid_header(short_buffer) is False
        long_buffer = bytes(range(10))
        assert is_valid_header(long_buffer) is False


class TestDistanceToValidHeader:
    def test_valid_headers(self) -> None:
        for msg_id in meta.msg_ids:
            buffer = FrameHeader(msg_id, rand_uint8(), rand_uint8(), rand_uint8()).buffer
            dist, chosen_id = hamming_distance_2_valid_header(buffer)
            assert dist == 0
            assert msg_id == chosen_id

    def test_corrupted_msg_id(self) -> None:
        for _ in range(500):
            msg = rand_msg()
            frame = FrameHeader(msg, rand_uint8(), rand_uint8(), rand_uint8())
            buffer = frame.buffer
            corrupted_msg = rand_msg()
            corrupted_buffer = buffer[:5] + bytes([corrupted_msg])

            dist_to_origin = hamming_distance(buffer, corrupted_buffer)  # originates from msg_id
            dist, chosen_msg = hamming_distance_2_valid_header(corrupted_buffer)

            chosen_frame = FrameHeader(chosen_msg, frame.sys_id, frame.comp_id, frame.sequence)
            dist_chosen = chosen_frame.hamming_distance(
                corrupted_buffer)  # distance originate from either length or msg_id fields
            assert dist_chosen == dist
            assert dist <= dist_to_origin

    def test_corrupted_len(self) -> None:
        for _ in range(500):
            msg = rand_msg()
            frame = FrameHeader(msg, rand_uint8(), rand_uint8(), rand_uint8())
            buffer = frame.buffer
            corrupted_len = rand_uint8()
            corrupted_buffer = bytes([buffer[0], corrupted_len]) + buffer[2:]

            dist_to_origin = hamming_distance(buffer, corrupted_buffer)  # originates from len
            dist, chosen_msg = hamming_distance_2_valid_header(corrupted_buffer)

            chosen_frame = FrameHeader(chosen_msg, frame.sys_id, frame.comp_id, frame.sequence)
            dist_chosen = chosen_frame.hamming_distance(
                corrupted_buffer)  # distance originate from either length or msg_id fields
            assert dist_chosen == dist
            assert dist <= dist_to_origin

    def test_corrupted_stx(self) -> None:
        for _ in range(500):
            msg = rand_msg()
            frame = FrameHeader(msg, rand_uint8(), rand_uint8(), rand_uint8())
            buffer = frame.buffer
            corrupted_stx = rand_uint8()
            corrupted_buffer = bytes([corrupted_stx]) + buffer[1:]

            dist_to_origin = hamming_distance(buffer, corrupted_buffer)  # originates from stx
            dist, chosen_msg = hamming_distance_2_valid_header(corrupted_buffer)  # chosen message should be the same as
            # original

            chosen_frame = FrameHeader(chosen_msg, frame.sys_id, frame.comp_id, frame.sequence)
            dist_chosen = chosen_frame.hamming_distance(
                corrupted_buffer)  # distance originate from either stx field
            assert dist_chosen == dist
            assert dist == dist_to_origin
            assert chosen_msg == msg

    def test_wrong_buffer_length(self) -> None:
        short_buffer = bytes(range(3))
        with pytest.raises(HeaderLength):
            hamming_distance_2_valid_header(short_buffer)
        long_buffer = bytes(range(10))
        with pytest.raises(HeaderLength):
            hamming_distance_2_valid_header(long_buffer)
