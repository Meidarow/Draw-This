from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from drawthis.core.protocols.protocols import DirEntryLike, Model

"""
This module defines all dataclasses used in the Session domain.
"""


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
class Session(Model):
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
