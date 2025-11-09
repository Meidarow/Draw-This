from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from iteradraw.domain.models.folder import FolderSet

if TYPE_CHECKING:
    pass
"""
This module defines all dataclasses used in the Session domain.

Classes:
    Session: Set of all parameters in a Draw-This resources.

Enums:
    Session.FIELDS: Reflects fields of Session, centralizing refactors.
    Session.DEFAULTS: Defines sane defaults for all fields of Session.
"""


@dataclass(frozen=True)
class Session:
    """
    Contain all parameters used for slideshow sessions

    Fields:
        selected_timer: Time during which a slide is SHOWN
        geometry: Size and position of the window for the slideshow
        is_running: Flag indicating whether a session is ongoing
    """

    class Fields(StrEnum):
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

    class Defaults:
        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080
        VERTICAL_OFFSET = 0  # vertical offset of TOP LEFT window corner
        HORIZONTAL_OFFSET = 0  # horizontal offset of TOP LEFT window corner
        SELECTED_TIMER = 0
        BREAK_TIMER = 0

    folders: FolderSet
    selected_timer: int = Defaults.SELECTED_TIMER
    break_timer: int = Defaults.BREAK_TIMER
    geometry: tuple[int, int, int, int] = (
        Defaults.SCREEN_WIDTH,
        Defaults.SCREEN_HEIGHT,
        Defaults.HORIZONTAL_OFFSET,
        Defaults.VERTICAL_OFFSET,
    )
    is_running: bool = False
