"""import csv data from experiment and write pickles"""
import csv
import pickle
from typing import TextIO, BinaryIO

binary_rx = []
file_t: TextIO
with open('rx.csv', 'r') as file_t:
    reader = csv.reader(file_t)
    for row in reader:
        try:
            while True:
                row.remove("")
        except ValueError:
            binary_rx.append([int(num) for num in row])


with open('rx_success.csv', 'r') as file_t:
    reader = csv.reader(file_t)
    for row in reader:
        rx_success = [int(num) for num in row]

binary_tx = []
with open('tx.csv', 'r') as file_t:
    reader = csv.reader(file_t)
    for row in reader:
        binary_tx.append([int(num) for num in row])

hc_to_ship = {"encoded_rx": binary_rx, "rx_success": rx_success, "encoded_tx": binary_tx}

file_b: BinaryIO
with open('hc_to_ship.pickle', 'wb') as file_b:
    pickle.dump(hc_to_ship, file_b)
