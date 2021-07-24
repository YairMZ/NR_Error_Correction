from enum import Enum


class MsgParts(Enum):
    HEADER = 0
    PAYLOAD = 1
    CHECKSUM = 2
    UNKNOWN = 3     # used when looking for header in corrupted data


class BufferSegmentation:
    """The class aims to break down a buffer to an ML sequence of MAVLink messages."""
    def __init__(self, msgs_len: dict):
        """
        :param msgs_len: a dictionary with msg_id as keys as messages length as values
        """
        self.msgs_len = msgs_len

    def parse_buffer(self, buffer: bytes) -> list:
        """
        Break down a buffer to several MAVLink messages.

        :param buffer: a buffer containing one or more MAVLink msgs
        :return: a list 
        """