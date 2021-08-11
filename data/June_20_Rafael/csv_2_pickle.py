import csv
import pickle
binary_rx = []
with open('rx.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            while True:
                row.remove("")
        except ValueError:
            binary_rx.append([int(num) for num in row])

with open('rx_success.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        rx_success = [int(num) for num in row]

binary_tx = []
with open('tx.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        binary_tx.append([int(num) for num in row])

hc_to_ship = {"encoded_rx": binary_rx, "rx_success": rx_success, "encoded_tx": binary_tx}

with open('hc_to_ship.pickle', 'wb') as file:
    pickle.dump(hc_to_ship, file)

