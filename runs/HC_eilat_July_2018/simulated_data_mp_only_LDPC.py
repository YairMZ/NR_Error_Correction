import pickle
from bitstring import Bits, BitArray
import numpy as np
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.decoder import bsc_llr, DecoderWiFi
import random
from multiprocessing import Pool
from numpy.typing import NDArray
from collections.abc import Sequence
from utils.bit_operations import hamming_distance
from typing import Any
import matplotlib.pyplot as plt
import argparse
import datetime
import os


def func(buffer: tuple[Sequence[int], float, int]) -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int]:
    """handler"""
    decoder = DecoderWiFi(bsc_llr(p=buffer[1]), spec=WiFiSpecCode.N1944_R23, max_iter=buffer[2])
    return decoder.decode(buffer[0])


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run decoding on simulated data using multiprocessing.')
    parser.add_argument("--N", default=0, help="max number of transmissions to consider", type=int)
    parser.add_argument("--minflip", default=3*1e-3, help="minimal bit flip probability to consider", type=float)
    parser.add_argument("--maxflip", default=1 * 1e-2, help="maximal bit flip probability to consider", type=float)
    parser.add_argument("--nflips", default=3, help="number of bit flips to consider", type=int)
    parser.add_argument("--niterations", default=5, help="number of iterations of of LDPC decoder", type=int)
    args = parser.parse_args()

    encoder = EncoderWiFi(WiFiSpecCode.N1944_R23)

    with open('data/hc_to_ship.pickle', 'rb') as f:
        hc_tx = pickle.load(f)

    five_sec_bin = [Bits(auto=tx.get("bin")) for tx in hc_tx.get("50000")]

    n = args.N if args.N > 0 else len(five_sec_bin)
    n_iterations = args.niterations

    # corrupt data
    rng = np.random.default_rng()
    bit_flip_p = np.linspace(args.minflip, args.maxflip, num=args.nflips)
    results: list[dict[str, Any]] = []

    for p in bit_flip_p:
        no_errors = int(encoder.n * p)
        encoded = []
        rx = []
        decoded_ldpc = []
        results.append({'data': five_sec_bin[:n]})

        for binary_data in five_sec_bin[:n]:
            # pad data - add 72 bits
            pad_len = encoder.k - len(binary_data)
            padded = binary_data + Bits(uint=random.getrandbits(pad_len), length=pad_len)
            encoded.append(encoder.encode(padded))
            corrupted = BitArray(encoded[-1])
            error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
            for idx in error_idx:
                corrupted[idx] = not corrupted[idx]
            rx.append(corrupted)
        with Pool() as pool:
            decoded_ldpc = pool.map(func, zip(rx, [p]*len(rx), [n_iterations]*len(rx)))
        results[-1]['encoded'] = encoded
        results[-1]['rx'] = rx
        results[-1]['decoded_ldpc'] = decoded_ldpc
        results[-1]["buffer_success_rate"] = sum([int(res[2]) for res in decoded_ldpc]) / float(n)
        results[-1]["raw_ber"] = no_errors / encoder.n
        results[-1]["buffer_len"] = len(encoded[0])
        results[-1]["decoder_ber"] = sum(
            hamming_distance(encoded[idx], Bits(auto=decoded_ldpc[idx][0])) for idx in range(n)
        ) / float(n * len(encoded[0]))
        print("successful decoding for bit flip probability p=", p, ", is: ", sum([int(res[2]) for res in decoded_ldpc]),
              "/", n)

    ber_vec = np.array([p['decoder_ber'] for p in results])
    plt.plot(bit_flip_p, ber_vec, 'bo', bit_flip_p, bit_flip_p, 'r^')
    plt.show()

    timestamp = str(datetime.date.today()) + "_" + str(datetime.datetime.now().hour) + "_" + str(
        datetime.datetime.now().minute)
    path = os.path.join("results/", timestamp)
    os.mkdir(path)

    with open(os.path.join(path, timestamp + '_simulation_only_LDPC.pickle'), 'wb') as f:
        pickle.dump(results, f)

    ber_vec = np.array([p['decoder_ber'] for p in results])
    fig = plt.figure()
    plt.plot(bit_flip_p, ber_vec, 'bo', bit_flip_p, bit_flip_p, 'r^')
    fig.savefig(os.path.join(path, "ber_vs_error_p.eps"), dpi=150)

    figure = plt.figure()
    buffer_success_rate = np.array([p['buffer_success_rate'] for p in results])
    plt.plot(bit_flip_p, buffer_success_rate, 'bo')
    figure.savefig(os.path.join(path, "buffer_success_rate_vs_error_p.eps"), dpi=150)
