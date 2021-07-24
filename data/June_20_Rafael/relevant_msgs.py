import pickle

with open('ship_rx.pickle', 'rb') as f:
    ship_rx = pickle.load(f)

# remove short messages (not containing a full mavlink message)
idx = 0
while idx < len(ship_rx["encoded"]):
    if len(ship_rx["encoded"][idx]) < 117:  # messages with actual mavlink are at least 117 byte long
        ship_rx["encoded"].pop(idx)
        ship_rx["rx_success"].pop(idx)
    else:
        # Since only first 117 bytes include MAVLink remove the rest
        ship_rx["encoded"][idx][117:] = []
        idx += 1

with open('preprocessed_rx.pickle', 'wb') as f:
    pickle.dump(ship_rx, f)
