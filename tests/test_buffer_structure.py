"""Unit tests for BufferStructure class"""
import pytest
from inference import BufferStructure

# setup test data
buffer1 = b'\xfe\x13\x00\x01\x00\xd4\x92\x01K\x16+G\xc0D+\xf4\n?\x00\x00\x80?<\t\x01\x896\xfe\n\x01\x01\x00\xda\x92' \
          b'\x01K\x16Z\x0c>\x10\x01d\xd0\xf5\xfe,\x02\x02\x00!\xd1\xffJ\x16\x12?\x97\x11\xb3"\xd2\x14\x00\x00\xc8B' \
          b'\x00\x00\xc8B\x00\x00\xc8B\xef\xfa\x10@\xbe\x1b^>\xb1\xd4\xda>\x05\x9d\xb8=D\x0b}BZ\xb9\xfe\x0c\x03\x01' \
          b'\xc8\xea\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb6r'
buffer2 = b'\xfe\x13\n\x01\x00\xd4jg\xd7\x16\rJ\xc0DQ\x9c=?\x00\x00@@?\t\x01\xd1\xdb\xfe\n\x0b\x01\x00\xdajg\xd7\x16c' \
          b'\x0c0\x10\x01d6\xdc\xfe,\x0c\x02\x00!\ne\xd7\x16\x858\x97\x11q\x10\xd2\x14\x00\x00\xc8B\x00\x00\xc8B\x00' \
          b'\x00\xc8BU\x91E@\x00\xacZ>\xe8t\xfb>\x8b\xf5\xdc=\x06A\x87BV%\xfe\x0c\r\x01\xc8\xea\x00\x00\x00\x00\x00' \
          b'\x00\x00\x00\x00\x00\x00\x00\xec\x92'


class TestBufferStructure:
    def test_equality(self) -> None:
        first_structure = BufferStructure({0: 212, 27: 218, 45: 33, 97: 234})
        second_structure = BufferStructure({0: 212, 27: 218, 45: 33, 97: 234})
        third_structure = BufferStructure({0: 212, 27: 218, 45: 33})
        first_structure.register_buffer(buffer1)
        second_structure.register_buffer(buffer2)
        assert first_structure == second_structure
        assert first_structure != third_structure
        assert first_structure == {0: 212, 27: 218, 45: 33, 97: 234}
        assert first_structure != 1

    def test_register_buffer(self) -> None:
        first_structure = BufferStructure({0: 212, 27: 218, 45: 33, 97: 234})
        first_structure.register_buffer(buffer1)
        assert first_structure.reception_count == 1
        with pytest.raises(ValueError):
            buffer = buffer1[::-1]  # reverse buffer breaks structure
            first_structure.register_buffer(buffer)

    def test_adheres_to_structure(self) -> None:
        structure = BufferStructure({0: 212, 27: 218, 45: 33, 97: 234})
        assert structure.adheres_to_structure(buffer1) is True
        structure = BufferStructure({0: 212, 27: 218, 45: 33, 97: 235})
        assert structure.adheres_to_structure(buffer1) is False

    def test_str(self) -> None:
        structure = BufferStructure({0: 212, 27: 218, 45: 33, 97: 234})
        assert str(structure) == '{0: 212, 27: 218, 45: 33, 97: 234}'

    def test_len(self) -> None:
        structure = BufferStructure({0: 212, 27: 218, 45: 33, 97: 234})
        assert len(structure) == 4
