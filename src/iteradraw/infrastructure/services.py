import uuid
from uuid import UUID

from iteradraw.application.handlers.interfaces import IdGenerator


class UUIDGenerator(IdGenerator):
    def generate(self) -> UUID:
        return uuid.uuid4()
