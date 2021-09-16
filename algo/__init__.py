"""Package for creating algorithms for error correction"""
from .correction_algorithm import CorrectionAlgorithm, AlgorithmType
from .entropy_algorithm import EntropyAlgorithm
__all__: list[str] = ["CorrectionAlgorithm", "AlgorithmType", "EntropyAlgorithm"]
