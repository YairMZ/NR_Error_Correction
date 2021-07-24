from __future__ import annotations


class KnownSender:
    """The class defines a known sender. Known senders comprise of a combination of sys_id and with comp_id sending a
    specific msg_id"""
    def __init__(self, sys_id: int, msg_id:int, comp_id: int):
        self.sys_id = sys_id
        self.msg_id = msg_id
        self.comp_id = comp_id
        self.msg_count = 1

    def __hash__(self):
        return hash((self.sys_id, self.msg_id, self.comp_id))

    def __eq__(self, other: KnownSender):
        return self.sys_id == other.sys_id and self.msg_id == other.msg_id and self.comp_id == other.comp_id

    def increase_count(self):
        self.msg_count += 1

    def __str__(self):
        return "system " + str(self.sys_id) + ", component " + str(self.comp_id) + ", msg " + str(self.msg_id)

    def __repr__(self):
        return str(self.sys_id) + "_" + str(self.comp_id) + "_ " + str(self.msg_id) + "_" + str(self.msg_count)


class Tokenizer:
    def __init__(self, known_senders: list[KnownSender] = None):
        if known_senders is None:
            known_senders = []
        self.known_senders: list[KnownSender] = known_senders

    def add_sender(self, sender: KnownSender):
        self.known_senders.append(sender)
