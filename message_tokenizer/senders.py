from __future__ import annotations


class KnownSender:
    """The class defines a known sender. Known senders are identified by sys_id. Each known sender is known to send
    specific msg_id from specific comp_id's"""

    def __init__(self, sys_id: int):
        self.sys_id = sys_id
        self.msg_id = {}  # keys are msg_id's, values are count
        self.comp_id = {}  # keys are comp_id's, values are count
        self.msg_count = 1  # overall msg count for sender
        self.msgs_log: dict() = {}  # overall message log for sender including msg_id, comp_id and and actual buffer.
        # Keys are comp_id, and values are dicts with keys as msg_ids. These dicts ave as value a list of buffers.
        # example: {comp_id1: {msg_id1: [buff1, buff2], msg_id2: [buff3, buff4, buff5]}}

    def __hash__(self):
        return hash(self.sys_id)

    def __eq__(self, other):
        if isinstance(other, KnownSender):
            return self.sys_id == other.sys_id
        if isinstance(other, int):
            return self.sys_id == other
        return False

    def register_msg(self, comp_id: int, msg_id: int, buffer: bytes):
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

    def __str__(self):
        return "system " + str(self.sys_id) + ", component " + str(self.comp_id) + ", msg " + str(self.msg_id)

    def __repr__(self):
        return str(self.sys_id) + "_" + str(self.msgs_log)
