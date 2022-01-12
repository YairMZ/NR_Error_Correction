"""import csv data from experiment and write pickles"""

import csv
import pickle
from typing import TextIO, BinaryIO
import bitstring
from utils.bit_operations import hamming_distance

encoded_rx = []
file_t: TextIO
with open('rx.csv', 'r') as file_t:
    reader = csv.reader(file_t)
    for row in reader:
        try:
            while True:
                row.remove("")
        except ValueError:
            encoded_rx.append([int(num) for num in row])

with open('rx_success.csv', 'r') as file_t:
    reader = csv.reader(file_t)
    for row in reader:
        rx_success = [int(num) for num in row]

encoded_tx = []
with open('tx.csv', 'r') as file_t:
    reader = csv.reader(file_t)
    for row in reader:
        encoded_tx.append([int(num) for num in row])

binary_rx: list[bitstring.Bits] = [bitstring.Bits()] * len(encoded_rx)
for idx, rx in enumerate(encoded_rx):
    binary_rx[idx] = bitstring.Bits(bytes=rx)

binary_tx: list[bitstring.Bits] = [bitstring.Bits()] * len(encoded_tx)
for idx, tx in enumerate(encoded_tx):
    binary_tx[idx] = bitstring.Bits(bytes=tx)

bit_errors: list[bitstring.Bits] = [bitstring.Bits()] * len(binary_tx)
num_of_bit_errors: list[int] = [0] * len(binary_tx)
for idx in range(len(binary_tx)):
    bit_errors[idx] = (binary_tx[idx]) ^ (binary_rx[idx])
    num_of_bit_errors[idx] = hamming_distance(binary_tx[idx], binary_rx[idx])

for idx in range(len(encoded_tx)):
    if rx_success[idx] == 1 and (encoded_tx[idx] != encoded_rx[idx] or num_of_bit_errors[idx] != 0):
        raise RuntimeError("Wrong rx_success encoding")

hc_to_ship = {"encoded_rx": encoded_rx, "rx_success": rx_success, "encoded_tx": encoded_tx, "binary_rx": binary_rx,
              "binary_tx": binary_tx, "bit_errors": bit_errors, "num_of_bit_errors": num_of_bit_errors,
              "number_tx": len(encoded_tx)}

file_b: BinaryIO
with open('hc_to_ship.pickle', 'wb') as file_b:
    pickle.dump(hc_to_ship, file_b)
