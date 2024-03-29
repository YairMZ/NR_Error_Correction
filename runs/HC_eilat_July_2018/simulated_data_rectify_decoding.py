"""rectifying decoder running script
This script doesn't enforce equal amount of iterations for all decoders for fairness.
"""
import pickle
from bitstring import Bits, BitArray
import numpy as np
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.decoder import bsc_llr, DecoderWiFi
from decoders import RectifyingDecoder, RectifyingDecoderSingleSegmentation
from inference import BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta

import random
from utils.bit_operations import hamming_distance
from typing import Any
import matplotlib.pyplot as plt
import argparse
import datetime
import os


parser = argparse.ArgumentParser(description='Run decoding on simulated data using multiprocessing.')
parser.add_argument("--N", default=0, help="max number of transmissions to consider", type=int)
parser.add_argument("--minflip", default=30*1e-3, help="minimal bit flip probability to consider", type=float)
parser.add_argument("--maxflip", default=45*1e-3, help="maximal bit flip probability to consider", type=float)
parser.add_argument("--nflips", default=3, help="number of bit flips to consider", type=int)
parser.add_argument("--ldpciterations", default=10, help="number of iterations of  LDPC decoder", type=int)
parser.add_argument("--segiterations", default=2, help="number of exchanges between LDPC and CB decoder", type=int)
parser.add_argument("--goodp", default=0, help="number of exchanges between LDPC and CB decoder", type=float)
parser.add_argument("--badp", default=0, help="number of exchanges between LDPC and CB decoder", type=float)

args = parser.parse_args()

ldpc_iterations = args.ldpciterations
seg_iter = args.segiterations
encoder = EncoderWiFi(WiFiSpecCode.N1944_R23)
bs = BufferSegmentation(meta.protocol_parser)

with open('data/hc_to_ship.pickle', 'rb') as f:
    hc_tx = pickle.load(f)

five_sec_bin = [Bits(auto=tx.get("bin")) for tx in hc_tx.get("50000")]
n = args.N if args.N > 0 else len(five_sec_bin)


# corrupt data
rng = np.random.default_rng()
bit_flip_p = np.linspace(args.minflip, args.maxflip, num=args.nflips)
results: list[dict[str, Any]] = []

encoded = []
for binary_data in five_sec_bin[:n]:
    pad_len = encoder.k - len(binary_data)
    padded = binary_data + Bits(uint=random.getrandbits(pad_len), length=pad_len)
    encoded.append(encoder.encode(padded))

n = len(encoded)

# encoded structure: {starting byte index in buffer: msg_id}
# {0: 33, 52: 234, 72: 30, 108: 212, 135: 218}
# last 9 bytes (72 bits) are padding and not messages. Thus last message ends at byte index 152
# bit indices:
# {0: 33, 416: 234, 576: 30, 864: 212, 1080: 218}

print("number of buffers to process: ", n)
print("smallest bit flip probability: ", args.minflip)
print("largest bit flip probability: ", args.maxflip)
print("number of bit flips: ", args.nflips)
print("number of ldpc decoder iterations: ", ldpc_iterations)
print("number of segmentation iterations: ", seg_iter)
print("good probability: ", args.goodp)
print("bad probability: ", args.badp)

for p in bit_flip_p:
    bad_p = args.badp if args.badp > 0 else 7*p  # this will make channel llr difference of close to 2 between default and bad
    good_p = args.goodp if args.goodp > 0 else p/7 # this will make channel llr diff of close to 2 between default and good
    ldpc_decoder = DecoderWiFi(bsc_llr(p=p), spec=WiFiSpecCode.N1944_R23, max_iter=ldpc_iterations)
    rectify_decoder = RectifyingDecoder(DecoderWiFi(bsc_llr(p=p), spec=WiFiSpecCode.N1944_R23, max_iter=ldpc_iterations),
                                seg_iter, ldpc_iterations, encoder.k, default_p=p, bad_p=bad_p, good_p=good_p)
    single_rect_decoder = RectifyingDecoderSingleSegmentation(DecoderWiFi(
        bsc_llr(p=p), spec=WiFiSpecCode.N1944_R23, max_iter=ldpc_iterations), encoder.k,
        default_p=p, bad_p=bad_p, good_p=good_p)
    no_errors = int(encoder.n * p)
    rx = []
    decoded_ldpc = []
    decoded_rectify = []
    decoded_single_rect = []
    results.append({'data': five_sec_bin[:n]})
    for tx_idx in range(n):
        # pad data - add 72 bits
        corrupted = BitArray(encoded[tx_idx])
        error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
        for idx in error_idx:
            corrupted[idx] = not corrupted[idx]
        rx.append(corrupted)
        d = ldpc_decoder.decode(corrupted)
        b = ldpc_decoder.info_bits(d[0]).tobytes()
        parts, v, s = bs.segment_buffer(b)
        decoded_ldpc.append((*d, len(s), hamming_distance(Bits(auto=d[0]), encoded[tx_idx])))
        if d[2] is False:
            print("pure ldpc, errors after decode: ", hamming_distance(Bits(auto=d[0]), encoded[tx_idx]))
        d = rectify_decoder.decode_buffer(corrupted)
        decoded_rectify.append((*d, hamming_distance(Bits(auto=d[0]), encoded[tx_idx])))
        if d[2] is False:
            print("rectified ldpc, errors after decode: ", hamming_distance(Bits(auto=d[0]), encoded[tx_idx]))
        d = single_rect_decoder.decode_buffer(corrupted)
        decoded_single_rect.append((*d, hamming_distance(Bits(auto=d[0]), encoded[tx_idx])))
        if d[2] is False:
            print("single rectified ldpc, errors after decode: ", hamming_distance(Bits(auto=d[0]), encoded[tx_idx]))
        print("tx id: ", tx_idx)
    print("successful pure decoding for bit flip p=", p, ", is: ", sum(int(res[5] == 0) for res in decoded_ldpc), "/", n)
    print("successful rectified decoding for bit flip p=", p, ", is: ", sum(int(res[5] == 0) for res in decoded_rectify), "/",
          n)
    print("successful single rectified decoding for bit flip p=", p, ", is: ",
          sum(int(res[5] == 0) for res in decoded_rectify), "/", n)
    results[-1]['encoded'] = encoded
    results[-1]['rx'] = rx
    results[-1]['decoded_ldpc'] = decoded_ldpc
    results[-1]["ldpc_buffer_success_rate"] = sum(int(res[5] == 0) for res in decoded_ldpc) / float(n)

    results[-1]["raw_ber"] = no_errors / encoder.n
    results[-1]["buffer_len"] = len(encoded[0])
    results[-1]["ldpc_decoder_ber"] = sum(
        hamming_distance(encoded[idx], Bits(auto=decoded_ldpc[idx][0]))
        for idx in range(n)
    ) / float(n * len(encoded[0]))

    results[-1]["decoded_rectified"] = decoded_rectify
    results[-1]["rectified_buffer_success_rate"] = sum(int(res[5] == 0) for res in decoded_rectify) / float(n)
    results[-1]["rectified_decoder_ber"] = sum(
        hamming_distance(encoded[idx], Bits(auto=decoded_rectify[idx][0]))
        for idx in range(n)
    ) / float(n * len(encoded[0]))

    results[-1]["decoded_single_rectified"] = decoded_single_rect
    results[-1]["single_rectified_buffer_success_rate"] = sum(int(res[5] == 0) for res in decoded_single_rect) / float(n)
    results[-1]["single_rectified_decoder_ber"] = sum(
        hamming_distance(encoded[idx], Bits(auto=decoded_single_rect[idx][0]))
        for idx in range(n)
    ) / float(n * len(encoded[0]))

    results[-1]["n"] = n
    results[-1]["max_ldpc_iterations"] = ldpc_iterations


timestamp = str(datetime.date.today()) + "_" + str(datetime.datetime.now().hour) + "_" + str(datetime.datetime.now().minute)
path = os.path.join("results/", timestamp)
os.mkdir(path)

with open(os.path.join(path, timestamp + '_simulation_rectify_vs_pure_LDPC.pickle'), 'wb') as f:
    pickle.dump(results, f)


raw_ber = np.array([p['raw_ber'] for p in results])
ldpc_ber = np.array([p['ldpc_decoder_ber'] for p in results])
rectified_ber = np.array([p['rectified_decoder_ber'] for p in results])
single_rect_ber = np.array([p['single_rectified_decoder_ber'] for p in results])
fig = plt.figure()
plt.plot(raw_ber, ldpc_ber, 'bo', raw_ber, raw_ber, 'g^', raw_ber, rectified_ber, 'r*')
fig.savefig(os.path.join(path, "ber_vs_error_p.eps"), dpi=150)

figure = plt.figure()
ldpc_buffer_success_rate = np.array([p['ldpc_buffer_success_rate'] for p in results])
rectified_buffer_success_rate = np.array([p['rectified_buffer_success_rate'] for p in results])
single_rect_buffer_success_rate = np.array([p['single_rectified_buffer_success_rate'] for p in results])
plt.plot(raw_ber, ldpc_buffer_success_rate, 'bo', raw_ber, rectified_buffer_success_rate, 'r*')
figure.savefig(os.path.join(path, "buffer_success_rate_vs_error_p.eps"), dpi=150)

summary = {"args": args, "raw_ber": raw_ber, "ldpc_ber": ldpc_ber, "rectified_ber": rectified_ber,
           "single_rect_ber":single_rect_ber, "single_rect_buffer_success_rate": single_rect_buffer_success_rate,
           "ldpc_buffer_success_rate": ldpc_buffer_success_rate,
           "rectified_buffer_success_rate": rectified_buffer_success_rate}
with open(os.path.join(path, timestamp + '_summary_rectify_vs_pure_LDPC.pickle'), 'wb') as f:
    pickle.dump(summary, f)
