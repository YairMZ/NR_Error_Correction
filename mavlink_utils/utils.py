from pymavlink.generator import mavgen  # type: ignore
from pymavlink.generator import mavparse


def dialect_creator(output_dialects_path: str, xml_path: str, protocol_language: str = mavgen.DEFAULT_LANGUAGE) -> None:
    """
    :param output_dialects_path: path for outputs
    :param xml_path: xml containing message definitions
    :param protocol_language: optional, language should be 'c' or 'python', defaults to 'python'
    """
    opts = mavgen.Opts(output_dialects_path,
                       wire_protocol=mavparse.PROTOCOL_1_0,
                       language=protocol_language,
                       validate=mavgen.DEFAULT_VALIDATE,
                       error_limit=mavgen.DEFAULT_ERROR_LIMIT,
                       strict_units=mavgen.DEFAULT_STRICT_UNITS)
    args = [xml_path]
    mavgen.mavgen(opts, args)


if __name__ == "__main__" and __package__ is None:
    from os import path, getcwd

    xml_defs_path = path.join(path.dirname(getcwd()), 'HC_dialect.xml')
    output_path = 'HC_dialect.py'

    dialect_creator(output_path, xml_defs_path)
