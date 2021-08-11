import data_generation.mavlink_utils.clustering_dialect as dialect
from data_generation.mavlink_utils.clustering_dialect import MAVError  # expose class directly to whomever imports meta

STX = dialect.PROTOCOL_MARKER_V1
field_lengths = {"uint32_t": 4, "float": 4, "uint16_t": 2, "uint8_t": 1, "int32_t": 4, }  # field length in bytes
msg_ids = list(dialect.mavlink_map.keys())
header_length = dialect.HEADER_LEN_V1
crc_length = 2
protocol_overhead = header_length + crc_length
# msgs_length = {msg_id: msg_len(msg_id) for msg_id in msg_ids}
# msgs_fields = {msg_id: msg_fields(msg_id) for msg_id in msg_ids}

#dialect_meta = MavlinkDialect(STX, header_length, crc_length, msg_ids, field_lengths)
