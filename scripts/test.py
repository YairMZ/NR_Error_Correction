from typing import Any
from inference import BufferSegmentation, MsgParts
from protocol_meta import dialect_meta as meta

import pickle
with open('../runs/June_20_Rafael/hc_to_ship.pickle', 'rb') as f:
    ship_rx = pickle.load(f)

good_transmissions = [buffer for is_success, buffer in zip(ship_rx["rx_success"], ship_rx["encoded_rx"])
                      if is_success == 1]
good_transmissions = [bytes(tx) for tx in good_transmissions]

bad_transmissions = [buffer for is_success, buffer in zip(ship_rx["rx_success"], ship_rx["encoded_rx"])
                     if is_success == 0]
bad_transmissions = [bytes(tx) for tx in bad_transmissions]

all_transmissions = [bytes(tx) for tx in ship_rx["encoded_rx"]]

bs = BufferSegmentation(meta.protocol_parser)
# for buffer in good_transmissions:
#     parts, validity, structure_ = bs.parse_buffer(buffer)
global_distance: list[Any] = []
valid_headers = 0
interesting_buffers = []
for idx, buffer in enumerate(all_transmissions):
    parts, validity, structure_ = bs.segment_buffer(buffer)
    if MsgParts.HEADER in parts and ship_rx["rx_success"][idx] == 0:  # if found at least one good message
        interesting_buffers.append(idx)
        print(len(structure_), " good messages")
        res = bs.bad_buffer_parts(buffer, parts)
print(len(interesting_buffers), " bad buffers with some good messages")
