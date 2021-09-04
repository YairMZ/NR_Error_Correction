import unittest
from protocol_meta.protocol_meta import dialect_meta as meta
from protocol_meta.msg_header import hamming_distance_2_valid_header, FrameHeader, is_valid_header, HeaderLength, \
    NonExistentMsdId
from utils.custom_exceptions import NonUint8
from utils.bit_operations import hamming_distance
from tests.random_test_data_generation import rand_msg, rand_uint8


class TestFrameHeader(unittest.TestCase):
    def test_wrong_msg_id(self):
        with self.subTest(msg="negative msg_id"):
            with self.assertRaises(NonUint8):
                FrameHeader(-1, rand_uint8(), rand_uint8(), rand_uint8())
        with self.subTest(msg="large msg_id"):
            with self.assertRaises(NonUint8):
                FrameHeader(256, rand_uint8(), rand_uint8(), rand_uint8())
        possible_ids = list(range(256))
        for msg_id in meta.msg_ids:
            possible_ids.remove(msg_id)
        if possible_ids:  # if there are illegal ids in dialect at all test them
            with self.subTest(msg="non existent msg_id"):
                with self.assertRaises(NonExistentMsdId):
                    FrameHeader(possible_ids[0], rand_uint8(), rand_uint8(), rand_uint8())

    def test_wrong_sys_id(self):
        with self.subTest(msg="negative sys_id"):
            with self.assertRaises(NonUint8):
                FrameHeader(rand_msg(), -1, rand_uint8(), rand_uint8())
        with self.subTest(msg="large sys_id"):
            with self.assertRaises(NonUint8):
                FrameHeader(rand_msg(), 256, rand_uint8(), rand_uint8())

    def test_wrong_comp_id(self):
        with self.subTest(msg="negative comp_id"):
            with self.assertRaises(NonUint8):
                FrameHeader(rand_msg(), rand_uint8(), -1, rand_uint8())
        with self.subTest(msg="large comp_id"):
            with self.assertRaises(NonUint8):
                FrameHeader(rand_msg(), rand_uint8(), 256, rand_uint8())

    def test_wrong_seq(self):
        with self.subTest(msg="negative seq"):
            with self.assertRaises(NonUint8):
                FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), -1)
        with self.subTest(msg="large seq"):
            with self.assertRaises(NonUint8):
                FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), 256)

    def test_hamming(self):
        mask = 1
        for i in range(6):
            with self.subTest():
                frame = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8())
                buffer = frame.buffer
                altered_buffer = buffer[:i] + bytes([buffer[i] ^ mask]) + buffer[i+1:]
                dist = frame.hamming_distance(altered_buffer)
                self.assertEqual(dist, i+1)
                mask = (mask << 1) + 1

    def test_hamming_wrong_length(self):
        frame = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8())
        buffer = frame.buffer
        self.assertRaises(HeaderLength, frame.hamming_distance, buffer+b"1")


class TestIsValidHeader(unittest.TestCase):
    def test_wrong_stx(self):
        buffer = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8()).buffer
        buffer = bytes([buffer[0] >> 1]) + buffer[1:]
        val = is_valid_header(buffer)
        self.assertFalse(val)

    def test_non_existent_msg_id(self):
        possible_ids = list(range(256))
        for msg_id in meta.msg_ids:
            possible_ids.remove(msg_id)
        if possible_ids:  # if there are illegal ids in dialect at all test them
            buffer = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8()).buffer
            buffer = buffer[:5] + bytes([possible_ids[0]])
            val = is_valid_header(buffer)
            self.assertFalse(val)
        else:
            self.assertTrue(True)

    def test_wrong_length(self):
        buffer = FrameHeader(rand_msg(), rand_uint8(), rand_uint8(), rand_uint8()).buffer
        buffer = bytes([buffer[0]]) + bytes([buffer[1] << 1]) + buffer[2:]
        val = is_valid_header(buffer)
        self.assertFalse(val)


class TestDistanceToValidHeader(unittest.TestCase):
    def test_valid_headers(self):
        for msg_id in meta.msg_ids:
            buffer = FrameHeader(msg_id, rand_uint8(), rand_uint8(), rand_uint8()).buffer
            dist, chosen_id = hamming_distance_2_valid_header(buffer)
            self.assertEqual(dist, 0)
            self.assertEqual(msg_id, chosen_id)

    def test_corrupted_msg_id(self):
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
            self.assertEqual(dist_chosen, dist)
            self.assertLessEqual(dist, dist_to_origin)

    def test_corrupted_len(self):
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
            self.assertEqual(dist_chosen, dist)
            self.assertLessEqual(dist, dist_to_origin)

    def test_corrupted_stx(self):
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
            self.assertEqual(dist_chosen, dist)
            self.assertEqual(dist, dist_to_origin)
            self.assertEqual(chosen_msg, msg)


if __name__ == '__main__':
    unittest.main()
