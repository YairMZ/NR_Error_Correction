import unittest
import bitstring  # type: ignore
from random_test_data_generation import rand_uint8, rand_bitstring
from utils.bit_operations import hamming_distance
import random


class TestHammingDistance(unittest.TestCase):
    def test_same_bitstrings(self):
        for _ in range(100):
            a = rand_bitstring(rand_uint8())
            d = hamming_distance(a, a)
            self.assertEqual(d, 0)

    def test_different_bitsrings(self):
        for _ in range(10):
            for i in range(1, 10):
                a = rand_bitstring(128)
                b = bitstring.BitArray(a)
                for pos in range(i):
                    b.invert(pos**2)
                self.assertEqual(hamming_distance(a, bitstring.Bits(b)), i)

    def test_byte_args(self):
        a = random.randbytes(128)
        b = bitstring.Bits(bytes=a)
        self.assertEqual(hamming_distance(a, b), 0)

    def test_uint8_args(self):
        a = rand_uint8()
        b = bitstring.Bits(uint=a, length=8)
        self.assertEqual(hamming_distance(a, b), 0)


if __name__ == '__main__':
    unittest.main()
