"""unit tests for the Known senders class"""
import pytest
from protocol_meta.protocol_meta import dialect_meta as meta
from message_tokenizer import KnownSender
from protocol_meta.msg_header import NonExistentMsdId
from utils.custom_exceptions import NonUint8


class TestKnownSender:
    def test_wrong_sys_id(self):
        # negative sys_id
        with pytest.raises(NonUint8):
            KnownSender(-1)
        # large sys_id
        with pytest.raises(NonUint8):
            KnownSender(256)

    def test_wrong_comp_id(self):
        a = KnownSender(0)
        msg_id = meta.msg_ids[0]
        # negative comp_id
        with pytest.raises(NonUint8):
            a.register_msg(-1, msg_id, b"")
        # large comp_id
        with pytest.raises(NonUint8):
            a.register_msg(256, msg_id, b"")

    def test_wrong_msg_id(self):
        a = KnownSender(0)
        # negative msg_id
        with pytest.raises(NonUint8):
            a.register_msg(0, -1, b"")
        # large msg_id
        with pytest.raises(NonUint8):
            a.register_msg(0, 256, b"")
        possible_ids = list(range(256))
        for msg_id in meta.msg_ids:
            possible_ids.remove(msg_id)
        # non existent msg_id
        if possible_ids:  # if there are illegal ids in dialect at all test them
            with pytest.raises(NonExistentMsdId):
                a.register_msg(0, possible_ids[0], b"")

    def test_hash_sender(self):
        assert 0 == hash(KnownSender(0))

    def test_repr(self):
        assert repr(KnownSender(0)) == "0_{}"

    def test_str(self):
        assert str(KnownSender(0)) == "system 0, component {}, msg {}"

    def test_register(self):
        a = KnownSender(0)
        a.register_msg(0, meta.msg_ids[0], b"\x00\x01")
        a.register_msg(0, meta.msg_ids[0], b"\x00\x01")
        assert a.msgs_log == {0: {0: [b'\x00\x01', b'\x00\x01']}}

    def test_equality(self):
        a = KnownSender(0)
        b = KnownSender(0)
        assert a == 0
        assert a == b
        assert a != "0"
