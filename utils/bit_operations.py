import bitstring


def hamming_distance(a: bitstring.Bits, b: bitstring.Bits) -> int:
    return (a ^ b).count(True)
