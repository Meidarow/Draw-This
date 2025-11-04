from abc import ABC, abstractmethod
from dataclasses import dataclass

from iteradraw.shared.types import PathLike


@dataclass(frozen=True)
class Model(ABC):
    """
    Model dataclasses are expected to be serializable into dicts for
    compatibility with the JSON persistence modules.
    """

    file_name: str
    settings_dir_path: PathLike

    @abstractmethod
    def to_dict(self):
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, dict):
        ...
