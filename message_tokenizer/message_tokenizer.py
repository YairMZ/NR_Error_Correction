from __future__ import annotations
from senders import KnownSender


class Tokenizer:
    def __init__(self, known_senders: list[KnownSender] = None):
        if known_senders is None:
            known_senders = []
        self.known_senders: list[KnownSender] = known_senders

    def add_sender(self, sender: KnownSender):
        self.known_senders.append(sender)
