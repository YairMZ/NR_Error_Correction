import bitstring
from typing import Union


def hamming_distance(a: Union[bitstring.Bits, bytes, int], b: Union[bitstring.Bits, bytes, int], uint_len=8) -> int:
    if isinstance(a, bytes):
        a = bitstring.Bits(bytes=a)
    if isinstance(b, bytes):
        b = bitstring.Bits(bytes=b)
    if isinstance(a, int):
        a = bitstring.Bits(uint=a, length=uint_len)
    if isinstance(b, int):
        b = bitstring.Bits(uint=b, length=uint_len)
    if not (isinstance(a, bitstring.Bits) and isinstance(b, bitstring.Bits)):
        raise TypeError()
    return (a ^ b).count(True)
