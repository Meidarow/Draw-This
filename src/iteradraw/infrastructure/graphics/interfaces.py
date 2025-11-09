from abc import ABC, abstractmethod

from iteradraw.domain.models.session import Session


class SlideshowBackend(ABC):
    @abstractmethod
    def start(self, session: Session):
        pass


class FehBackend(SlideshowBackend):
    def start(self, session: Session = None):
        start_slideshow_feh(**session.to_dict())


class OGLBackend(SlideshowBackend):
    def start(self, session: Session = None):
        start_slideshow_ogl(**session.to_dict())
