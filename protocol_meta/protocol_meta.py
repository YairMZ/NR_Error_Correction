"""meta data of specific mavlink dialect"""
import mavlink_utils.HC_dialect as dialect
from mavlink_utils.HC_dialect import MAVError  # expose class directly to whomever imports meta
from typing import Callable
from collections.abc import MutableSequence

STX = dialect.PROTOCOL_MARKER_V1
field_lengths = {"uint32_t": 4, "float": 4, "uint16_t": 2, "uint8_t": 1, "int32_t": 4, "int16_t": 2, "int8_t": 1,
                 "uint64_t": 8, "char": 1, "int64_t": 8}  # field length in bytes
msg_ids = list(dialect.mavlink_map.keys())
header_length = dialect.HEADER_LEN_V1
crc_length = 2
protocol_overhead = header_length + crc_length


class MavlinkDialectMeta:
    """This class describes the structure of a general Mavlink dialect"""
    def __init__(self, stx: int,  header_len: int, crc_len: int, msg_ids_: list[int], field_lengths_: dict[str, int],
                 protocol_parser: Callable[[MutableSequence[int]], object]):
        self.stx: int = stx
        self.header_len: int = header_len
        self.crc_len: int = crc_len
        self.msg_ids: list[int] = msg_ids_
        self.field_lengths: dict[str, int] = field_lengths_
        self.protocol_overhead: int = header_len + crc_len
        self.msgs_length: dict[int, int] = {msg_id: self.__msg_len(msg_id) for msg_id in msg_ids_}
        self.msgs_fields: dict[int, list[tuple[str, str]]] = {msg_id: self.__msg_fields(msg_id) for msg_id in msg_ids_}
        self.protocol_parser = protocol_parser

    @staticmethod
    def __msg_fields(msg_id: int) -> list[tuple[str, str]]:
        """Given a msg_id, this function returns a list of tuples. Each tuple has the form (field_name, field_type),
        where field_name is a string, and field_type is a string representation of the type
        The list is ordered according to the over the air order used by the protocol. For details see:
        https://mavlink.io/en/guide/serialization.html#field_reordering
        """
        obj: type = dialect.mavlink_map.get(msg_id)  # type: ignore
        if not issubclass(obj, dialect.MAVLink_message):
            raise ValueError()
        num_of_fields = len(obj.fieldnames)  # type: ignore
        unordered_fieldnames = {
            obj.fieldnames[i]: obj.fieldtypes[i]  # type: ignore
            for i in range(num_of_fields)}
        ordered_fieldnames: list[str] = obj.ordered_fieldnames  # type: ignore
        fields: list[tuple[str, str]] = [("", "")] * num_of_fields
        for i in range(num_of_fields):
            fields[i] = (ordered_fieldnames[i], unordered_fieldnames.get(ordered_fieldnames[i], ""))
        return fields

    def __msg_len(self, msg_id: int) -> int:
        obj: type = dialect.mavlink_map.get(msg_id)  # type: ignore
        if not issubclass(obj, dialect.MAVLink_message):
            raise ValueError()
        field_types = obj.fieldtypes  # type: ignore
        return sum(self.field_lengths[field] for field in field_types)


mav_obj = dialect.MAVLink(1)
dialect_meta = MavlinkDialectMeta(STX, header_length, crc_length, msg_ids, field_lengths, mav_obj.decode)
__all__ = ["MAVError", "dialect_meta"]
