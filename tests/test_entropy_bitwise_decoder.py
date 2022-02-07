"""unit tests for the EntropyBitwiseDecoder class"""
import pytest
import numpy as np
import bitstring
from utils.custom_exceptions import IncorrectBufferLength
from decoders import EntropyBitwiseDecoder
from ldpc.decoder import bsc_llr, DecoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode


class TestEntropyBitwiseDecoder:
    def test_wrong_buffer_length(self) -> None:
        entropy_decoder = EntropyBitwiseDecoder(DecoderWiFi(spec=WiFiSpecCode.N1944_R23, max_iter=10),
                                                model_length=10, entropy_threshold=1)
        buffer = np.unpackbits(np.array(list(range(10)), dtype=np.uint8))
        with pytest.raises(Exception):
            entropy_decoder.decode_buffer(buffer)

    def test_wrong_model_length(self) -> None:
        entropy_decoder = EntropyBitwiseDecoder(DecoderWiFi(spec=WiFiSpecCode.N1944_R23, max_iter=10),
                                                model_length=10, entropy_threshold=1)
        with pytest.raises(IncorrectBufferLength):
            entropy_decoder.update_model(np.array([1]))
