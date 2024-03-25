from dataclasses import make_dataclass
from typing import Type, Any


def convert_to_dataclass(cls: Type, d: dict) -> Any:
    """
    Converts the dict object to an instance of the given DataClass
    :param cls: name of the data class to convert to.
    :param d: dictionary to convert.
    :return:
    """
    return make_dataclass(cls.__name__, ((k, type(v)) for k, v in d.items()))(**d)
