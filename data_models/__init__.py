"""package init for all data models"""
from .data_model import DataModel, ModelType
from .entropy_model import EntropyModel
__all__: list[str] = ["DataModel", "ModelType", "EntropyModel"]
