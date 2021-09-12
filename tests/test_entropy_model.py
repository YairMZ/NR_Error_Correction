"""unit tests for the Entropy model class"""
import pytest
import numpy as np
import bitstring  # type: ignore
from utils.custom_exceptions import IncorrectBufferLength, UnsupportedDtype
from data_models import EntropyModel


class TestEntropyModel:
    def test_unsupported_dtype(self):
        with pytest.raises(UnsupportedDtype):
            EntropyModel(10, element_type="float")

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
        buffer = buffer[:5] + (bitstring.Bits(bytes=buffer[5:]) ^ bitstring.Bits(bytes=b"\xFF" * 5)).bytes
        model.update_model(buffer)
        e = model.entropy
        np.testing.assert_allclose(e, np.array(([0.0] * 40) + [1.0] * 40))
        assert model.data.shape == (80, 2)

    def test_infer_structure(self):
        data = [bytes(list(range(10)) + list(range(i, i+10))) for i in range(10)]
        model = EntropyModel(len(data[0]), False)
        for datum in data:
            model.update_model(datum)
        model.infer_structure(entropy_threshold=1)
        structural_elements, structural_elements_values = model.get_structure()
        np.testing.assert_array_equal(structural_elements, np.array(range(10)))
        np.testing.assert_allclose(structural_elements_values, np.array(range(10)))

    def test_predict(self):
        data = [bytes(list(range(10)) + list(range(i, i + 10))) for i in range(10)]
        model = EntropyModel(len(data[0]), bitwise=False)
        for datum in data:
            model.update_model(datum)
        bad_data = bytes([20]) + data[1][1:]
        # verify exception
        with pytest.raises(ValueError):
            model.predict(bad_data)
        # predict first byte (corrupted)
        prediction, ent = model.predict(bad_data, entropy_threshold=1.0)
        assert prediction == data[1]

    def test_predict_bitwise(self):
        data = [bytes(list(range(10)) + list(range(i, i + 10))) for i in range(10)]
        model = EntropyModel(len(data[0]))
        for datum in data:
            model.update_model(datum)
        bad_data = bytes([20]) + data[1][1:]
        # predict first byte (corrupted)
        prediction, ent = model.predict(bad_data, entropy_threshold=0.1)
        assert prediction == data[1]

    def test_predict_int32(self):
        data = [bytes(list(range(12)) + list(range(3 * i, 3 * i + 12))) for i in range(10)]
        model = EntropyModel(len(data[0]), bitwise=False, element_type="int32")
        for datum in data:
            model.update_model(datum)
        bad_data = bytes([20]) + data[1][1:]
        # predict first byte (corrupted)
        prediction, ent = model.predict(bad_data, entropy_threshold=1)
        assert prediction == data[1]

    def test_finite_window(self):
        data = [bytes(list(range(12)) + list(range(3 * i, 3 * i + 12))) for i in range(10)]
        window_length = 5
        model = EntropyModel(len(data[0]), bitwise=False, element_type="int32", window_length=window_length)
        for datum in data:
            model.update_model(datum)
        assert model.data.shape[1] == window_length
