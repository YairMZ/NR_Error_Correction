import data_generation.mavlink_utils.clustering_dialect as dialect
from data_generation.mavlink_utils.clustering_dialect import MAVError  # expose class directly to whomever imports meta
from typing import Callable

STX = dialect.PROTOCOL_MARKER_V1
field_lengths = {"uint32_t": 4, "float": 4, "uint16_t": 2, "uint8_t": 1, "int32_t": 4, }  # field length in bytes
msg_ids = list(dialect.mavlink_map.keys())
header_length = dialect.HEADER_LEN_V1
crc_length = 2
protocol_overhead = header_length + crc_length


class MavlinkDialectMeta:
    """This class describes the structure of a general Mavlink dialect"""
    def __init__(self, stx: int,  header_len: int, crc_len: int, msg_ids_: list, field_lengths_: dict,
                 protocol_parser: Callable):
        self.stx: int = stx
        self.header_len: int = header_len
        self.crc_len: int = crc_len
        self.msg_ids: list = msg_ids_
        self.field_lengths: dict = field_lengths_
        self.protocol_overhead: int = header_len + crc_len
        self.msgs_length: dict = {msg_id: self.__msg_len(msg_id) for msg_id in msg_ids}
        self.msgs_fields: dict = {msg_id: self.__msg_fields(msg_id) for msg_id in msg_ids}
        self.protocol_parser: Callable = protocol_parser

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

mav_obj = dialect.MAVLink(1)
dialect_meta = MavlinkDialectMeta(STX, header_length, crc_length, msg_ids, field_lengths, mav_obj.decode)
