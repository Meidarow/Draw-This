import random
from dataclasses import dataclass, field
from enum import StrEnum
from typing import (
    NamedTuple,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from drawthis.core.protocols.protocols import DirEntryLike

"""
This module defines all dataclasses used in the Session domain.
"""

# =============================================================================
# Session - Persistence and Database dataclasses
# =============================================================================


@dataclass
class FileStat:
    st_mtime: float
    st_ino: int
    st_dev: int


@dataclass(frozen=True)
class FileEntry:
    path: str
    is_dir: bool
    is_symlink: bool
    stat: "FileStat"

    @classmethod
    def from_dir_entry(cls, dir_entry: "DirEntryLike") -> "FileEntry":
        """
        Return a FileEntry object

        Args:
            dir_entry DirEntryLike: filesystem object

        Returns:
            FileEntry: Canonical file-system dataclass for Draw-This

        Notes:
            This method caches a DirEntryLike's attributes into a FileEntry
            directly to minimise syscalls in the database layer.
        """
        stat = dir_entry.stat()
        return cls(
            path=dir_entry.path,
            is_dir=dir_entry.is_dir(),
            is_symlink=dir_entry.is_symlink(),
            stat=FileStat(
                st_mtime=stat.st_mtime,
                st_ino=stat.st_ino,
                st_dev=stat.st_dev,
            ),
        )


class ImageRow(NamedTuple):
    """
    Dataclass containing all fields for the slideshow backend solution.
    The resources domain's persistence layer only uses this object type
    internally.

    This object defines all the fields or columns that MUST be present in an
    implementation of the SessionPersistence backend classes.
    """

    file_path: str
    randid: float
    mtime: float

    @classmethod
    def from_file_entry(cls, file_entry: "FileEntry") -> "ImageRow":
        """
        Return an ImageRow object

        Args:
            file_entry FileEntry: Canonical file-system object for Draw-This

        Returns:
            ImageRow: Canonical database object for Draw-This
        """
        return ImageRow(
            file_path=file_entry.path,
            randid=random.random(),
            mtime=file_entry.stat.st_mtime,
        )


# =============================================================================
# Session - Intra slideshow domain
# =============================================================================

"""
This module holds the definitions for all dataclasses used by the
SlideshowService.

Dataclasses:
-Session: Set of all parameters in a Draw-This resources

Enums:
-SESSION.FIELDS: Reflects fields of Session, centralizing refactors
-SESSION.DEFAULTS: Defines sane defaults for all fields of Session
"""


class SESSION:
    class FIELDS(StrEnum):
        """
        Define field keys and sane defaults for Session.

        New fields may be added by:
          - Adding it here AND in Session as follows:
          ENUM_FIELD_NAME = "session_attribute_name"
        """

        SLIDE_TIMER = "selected_timer"
        BREAK_TIMER = "break_timer"
        WINDOW_GEOMETRY = "geometry"
        IS_RUNNING_FLAG = "is_running"
        ADDED_FOLDERS = "folders_to_add"
        REMOVED_FOLDERS = "folders_to_remove"

    class DEFAULTS:
        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080
        VERTICAL_OFFSET = 0  # vertical offset of TOP LEFT window corner
        HORIZONTAL_OFFSET = 0  # horizontal offset of TOP LEFT window corner
        SELECTED_TIMER = 0
        BREAK_TIMER = 0


@dataclass(frozen=True)
class Session:
    """
    Contain all parameters used for slideshow sessions

    Fields:
        selected_timer: Time during which a slide is SHOWN
        geometry: Size and position of the window for the slideshow
        is_running: Flag indicating whether a resources is ongoing
    """

    selected_timer: int = SESSION.DEFAULTS.SELECTED_TIMER
    break_timer: int = SESSION.DEFAULTS.BREAK_TIMER
    folders_to_add: list[str] = field(default_factory=list)
    folders_to_remove: list[str] = field(default_factory=list)
    geometry: tuple[int, int, int, int] = (
        SESSION.DEFAULTS.SCREEN_WIDTH,
        SESSION.DEFAULTS.SCREEN_HEIGHT,
        SESSION.DEFAULTS.HORIZONTAL_OFFSET,
        SESSION.DEFAULTS.VERTICAL_OFFSET,
    )
    is_running: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Session":
        """
        Iterate over expected fields of a Session, specified in SessionFields,
        and retrieves it from input dict. If not found, insert attribute
        default value as defined in Session.

        This allows for automatic synchronicity between the SessionFields
        and the Session constructor/converter methods.
        Args:
            d: input dict with values to be inserted into Session

        Returns:
            A Session instance with fields matching SessionFields. Always
            instantiated with sane defaults for missing values.
        """
        kwargs = {}
        for field in SESSION.FIELDS:
            attribute_name = field
            kwargs[attribute_name] = d.get(field, getattr(cls, attribute_name))
        return cls(**kwargs)

    def to_dict(self) -> dict:
        """
        Iterate over expected fields of a Session, specified in SessionFields,
        and generate output dict.

        This allows for automatic synchronicity between the SessionFields
        and the Session constructor/converter methods.

        Returns:
            A Dict with keys matching SessionFields.
        """
        return {field: getattr(self, field) for field in SESSION.FIELDS}

    def copy(self) -> "Session":
        """Return identical separate instance of current Session"""
        return Session(**self.to_dict())
