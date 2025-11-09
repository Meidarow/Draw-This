class SlideshowManager:
    """
    High-level controller for slideshow backends.

    This class provides a unified API for the frontend (ViewModel/GUI) to
    control slideshow lifecycle, regardless of the rendering backend.

    Responsibilities:
    - Start and stop the slideshow window.
    - Report whether a slideshow resources is currently active.
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

    def __init__(self, backend: SlideshowBackend = None):
        self.backend = backend or FehBackend()

    def start(self, session: Session):
        self.backend.start(session)

    def stop(self):
        pass

    @property
    def is_running(self):
        return

    # Private helpers
