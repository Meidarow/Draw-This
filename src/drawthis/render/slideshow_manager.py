from drawthis.gui.state import Session


class SlideshowManager:
    """
    High-level controller for slideshow backends.

    This class provides a unified API for the frontend (ViewModel/GUI) to
    control slideshow lifecycle, regardless of the rendering backend.

    Responsibilities:
    - Start and stop the slideshow window.
    - Report whether a slideshow session is currently active.
    - Provide hooks for backend-specific implementations (FEH, ModernGL).

    Usage:
        manager = SlideshowManager()
        manager.start_slideshow()
        if manager.slideshow_is_running:
            ...

    Extending:
        Subclass or inject a backend adapter implementing the same API
        to support additional backends.
    """

    def __init__(self):
        pass

    def start(self, session: Session):
        pass

    def stop(self):
        pass

    @property
    def is_running(self):
        pass

    # Private helpers
