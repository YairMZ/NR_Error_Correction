"""The package contains all the relevant meta data regarding a protocol."""
from .protocol_meta import MAVError
from .protocol_meta import dialect_meta as dialect_meta
from .msg_header import hamming_distance_2_valid_header, FrameHeader, is_valid_header, NonExistentMsdId
