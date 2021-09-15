"""unit tests for bit_operations module within the utils package"""
import pytest
import bitstring
from data_generation.random_test_data_generation import rand_uint8, rand_bitstring
from utils.bit_operations import hamming_distance
import random


class TestHammingDistance:
    def test_same_bitstrings(self) -> None:
        for _ in range(100):
            a = rand_bitstring(rand_uint8())
            d = hamming_distance(a, a)
            assert d == 0

    def test_different_bitsrings(self) -> None:
        for _ in range(10):
            for i in range(1, 10):
                a = rand_bitstring(128)
                b = bitstring.BitArray(a)
                for pos in range(i):
                    b.invert(pos**2)
                assert hamming_distance(a, bitstring.Bits(b)) == i

    def test_byte_args(self) -> None:
        a = random.randbytes(128)
        b = bitstring.Bits(bytes=a)
        assert hamming_distance(a, b) == 0

    def test_uint8_args(self) -> None:
        a = rand_uint8()
        b = bitstring.Bits(uint=a, length=8)
        assert hamming_distance(a, b) == 0

    def test_wrong_types(self) -> None:
        a = '0011 00'
        b = bitstring.Bits(bin=a)
        with pytest.raises(TypeError):
            hamming_distance(a, b)
