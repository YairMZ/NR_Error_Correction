from protocol_meta import dialect_meta as meta
from decoders import EntropyDecoder
from inference import BufferSegmentation, MsgParts

import pickle


with open('../data/June_20_Rafael/hc_to_ship.pickle', 'rb') as f:
    ship_rx = pickle.load(f)

good_transmissions = [buffer for is_success, buffer in zip(ship_rx["rx_success"], ship_rx["encoded_rx"])
                      if is_success == 1]
good_transmissions = [bytes(tx) for tx in good_transmissions]

bad_transmissions = [buffer for is_success, buffer in zip(ship_rx["rx_success"], ship_rx["encoded_rx"])
                     if is_success == 0]
bad_transmissions = [bytes(tx) for tx in bad_transmissions]

all_transmissions = [bytes(tx) for tx in ship_rx["encoded_rx"]]

decoder = EntropyDecoder()
bs = BufferSegmentation(meta.protocol_parser)
interesting_buffers = []
for idx, buffer in enumerate(all_transmissions):
    parts, validity, structure = bs.segment_buffer(buffer)
    decoded, success = decoder.decode_buffer(buffer)
    if MsgParts.HEADER in parts and MsgParts.UNKNOWN in parts:  # if found at least one good message
        interesting_buffers.append(idx)
        print(len(structure), " good messages")
        res = bs.bad_buffer_idx(buffer, parts)
        parts, validity, decoded_structure = bs.segment_buffer(decoded)
        if decoded_structure != structure:
            print("corrected a message")


print(len(interesting_buffers), " bad buffers with some good messages")
