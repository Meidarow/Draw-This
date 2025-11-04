from dataclasses import dataclass


@dataclass(frozen=True)
class AddFolderCommand:
    folder_path: str
    enabled: bool


@dataclass(frozen=True)
class RemoveFolderCommand:
    folder_path: str
