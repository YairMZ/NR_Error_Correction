import random

import bitstring  # type: ignore

from protocol_meta.protocol_meta import dialect_meta as meta


def rand_uint8():
    return random.randint(0, 255)


def rand_msg():
    return random.choice(meta.msg_ids)


def rand_bitstring(n):
    ls = [random.randint(0, 1) for _ in range(n)]
    s = "".join(map(str, ls))
    return bitstring.Bits(bin=s)
