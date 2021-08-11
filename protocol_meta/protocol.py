from .protocol_meta import dialect, STX, header_length, crc_length, msg_ids, field_lengths


class MavlinkDialect:
    """This class describes the structure of a general Mavlink dialect"""
    def __init__(self, stx: int,  header_len: int, crc_len: int, msg_ids: list, field_lengths):
        self.stx = stx
        self.header_len = header_len
        self.crc_len = crc_len
        self.msg_ids = msg_ids
        self.field_lengths = field_lengths
        self.protocol_overhead = header_len + crc_len
        self.msgs_length = {msg_id: self.__msg_len(msg_id) for msg_id in msg_ids}
        self.msgs_fields = {msg_id: self.__msg_fields(msg_id) for msg_id in msg_ids}

    @staticmethod
    def __msg_fields(msg_id: int) -> list:
        """Given a msg_id, this function returns a list of tuples. Each tuple has the form (field name, field type).
        The list is ordered according to the over the air order used by the protocol. For details see:
        https://mavlink.io/en/guide/serialization.html#field_reordering
        """
        num_of_fields = len(dialect.mavlink_map.get(msg_id).fieldnames)
        unordered_fieldnames = {
            dialect.mavlink_map.get(msg_id).fieldnames[i]: dialect.mavlink_map.get(msg_id).fieldtypes[i]
            for i in range(num_of_fields)}
        ordered_fieldnames = dialect.mavlink_map.get(msg_id).ordered_fieldnames
        fields = [None] * num_of_fields
        for i in range(num_of_fields):
            fields[i] = (ordered_fieldnames[i], unordered_fieldnames.get(ordered_fieldnames[i]))
        return fields

    def __msg_len(self, msg_id: int) -> int:
        field_types = dialect.mavlink_map.get(msg_id).fieldtypes
        length = 0
        for field in field_types:
            length += self.field_lengths[field]
        return length


dialect_meta = MavlinkDialect(STX, header_length, crc_length, msg_ids,
                              field_lengths)
