from pathlib import Path
from typing import Iterable

# Type aliases

PathLike = str | Path
FolderInput = PathLike | Iterable[PathLike]

# Static dataclasses
