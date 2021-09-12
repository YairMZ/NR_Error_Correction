"""utility functions used throughout tests"""
import random

import bitstring  # type: ignore

from protocol_meta.protocol_meta import dialect_meta as meta


def rand_uint8():
    """generate a random uint8 value"""
    return random.randint(0, 255)


def rand_msg():
    """generate a random msg id from allowed id's as specified in the protocol meta"""
    return random.choice(meta.msg_ids)


def rand_bitstring(n):
    """generate a random bitstring of n bits"""
    ls = [random.randint(0, 1) for _ in range(n)]
    s = "".join(map(str, ls))
    return bitstring.Bits(bin=s)
