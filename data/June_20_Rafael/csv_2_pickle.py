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

ship_rx = {"encoded": binary_rx, "rx_success": rx_success}

with open('ship_rx.pickle', 'wb') as file:
    pickle.dump(ship_rx, file)

