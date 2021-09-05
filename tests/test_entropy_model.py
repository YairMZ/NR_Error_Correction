import pytest
import numpy as np
import bitstring
from utils.custom_exceptions import IncorrectBufferLength
from data_models import EntropyModel


class TestEntropyModel:
    def test_update_model_wrong_length(self):
        model = EntropyModel(10)
        buffer = bytes(range(7))
        with pytest.raises(IncorrectBufferLength):
            model.update_model(buffer)

    def test_update_model(self):
        """use a simple distribution to check entropy"""
        model = EntropyModel(10)
        buffer = bytes(range(10))
        model.update_model(buffer)
        # now flip last half of bits
        buffer = buffer[:5] + (bitstring.Bits(bytes=buffer[5:]) ^ bitstring.Bits(bytes=b"\xFF"*5)).bytes
        model.update_model(buffer)
        e = model.entropy
        np.testing.assert_allclose(e, np.array(([0.0]*40)+[1.0]*40))
