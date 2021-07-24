import data_generation.mavlink_utils.clustering_dialect as dialect

STX = b"\xFE"
field_lengths = {"uint32_t": 4, "float": 4, "uint16_t": 2, "uint8_t": 1, "int32_t": 4, }  # field length in bytes
msg_ids = list(dialect.mavlink_map.keys())


def msg_len(msg_id: int) -> int:
    field_types = dialect.mavlink_map.get(msg_id).fieldtypes
    length = 0
    for field in field_types:
        length += field_lengths[field]
    return length


def msg_fields(msg_id: int) -> list:
    """Given a msg_id, this function returns a list of tuples. Each tuple has the form (field name, field type).
    The list is ordered according to the over the air order used by the protocol. For details see:
    https://mavlink.io/en/guide/serialization.html#field_reordering
    """
    num_of_fields = len(dialect.mavlink_map.get(msg_id).fieldnames)
    unordered_fieldnames = {dialect.mavlink_map.get(msg_id).fieldnames[i]: dialect.mavlink_map.get(msg_id).fieldtypes[i]
                            for i in range(num_of_fields)}
    ordered_fieldnames = dialect.mavlink_map.get(msg_id).ordered_fieldnames
    fields = [None]* num_of_fields
    for i in range(num_of_fields):
        fields[i] = (ordered_fieldnames[i], unordered_fieldnames.get(ordered_fieldnames[i]))
    return fields


msgs_length = {msg_id: msg_len(msg_id) for msg_id in msg_ids}
msgs_fields = {msg_id: msg_fields(msg_id) for msg_id in msg_ids}
