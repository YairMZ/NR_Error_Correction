"""class for holding known senders, and information regarding them"""
from protocol_meta import dialect_meta as meta, NonExistentMsdId
from utils.custom_exceptions import NonUint8


class KnownSender:
    """The class defines a known sender. Known senders are identified by sys_id. Each known sender is known to send
    specific msg_id from specific comp_id's"""

    def __init__(self, sys_id: int):
        if sys_id < 0 or sys_id > 255:
            raise NonUint8("invalid input, msg_id: {}".format(sys_id))
        self.sys_id: int = sys_id
        self.msg_id: dict = {}  # keys are msg_id's, values are count
        self.comp_id: dict = {}  # keys are comp_id's, values are count
        self.msg_count: int = 0  # overall msg count for sender
        self.msgs_log: dict = {}  # overall message log for sender including msg_id, comp_id and and actual buffer.
        # Keys are comp_id, and values are dicts with keys as msg_ids. These dicts ave as value a list of buffers.
        # example: {comp_id1: {msg_id1: [buff1, buff2], msg_id2: [buff3, buff4, buff5]}}

    def __hash__(self) -> int:
        return hash(self.sys_id)

    def __eq__(self, other) -> bool:
        if isinstance(other, KnownSender):
            return self.sys_id == other.sys_id
        if isinstance(other, int):
            return self.sys_id == other
        return False

    def register_msg(self, comp_id: int, msg_id: int, buffer: bytes) -> None:
        """
        register a received message for this sender.

        :param comp_id: component id of sender
        :param msg_id: msg id of sender
        :param buffer: actual buffer of containing message
        """
        if comp_id < 0 or comp_id > 255:
            raise NonUint8("invalid input, comp_id: {}".format(comp_id))
        if msg_id < 0 or msg_id > 255:
            raise NonUint8(msg_id)
        elif msg_id not in meta.msgs_length.keys():
            raise NonExistentMsdId("msg_id {} does not exist".format(msg_id))

        if comp_id not in self.comp_id:
            self.comp_id[comp_id] = 1
            self.msgs_log[comp_id] = {}
        else:
            self.comp_id[comp_id] += 1
        if msg_id not in self.msg_id:
            self.msg_id[msg_id] = 1
        else:
            self.msg_id[msg_id] += 1
        if msg_id not in self.msgs_log[comp_id]:
            self.msgs_log[comp_id][msg_id] = [buffer]
        else:
            self.msgs_log[comp_id][msg_id].append(buffer)
        self.msg_count += 1

    def __str__(self) -> str:
        return "system " + str(self.sys_id) + ", component " + str(self.comp_id) + ", msg " + str(self.msg_id)

    def __repr__(self) -> str:
        return str(self.sys_id) + "_" + str(self.msgs_log)
