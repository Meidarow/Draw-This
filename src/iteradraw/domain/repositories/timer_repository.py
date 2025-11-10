from typing import Callable

from iteradraw.domain.models.timer import TimerSet


class TimerRepository:
    """
    Repository for TimerSet domain objects.

    Facilitates persistence operations for the TimerSet model by
    abstracting backend implementations and providing (de-)serialization
    methods. Allows for backend injection, as long as implementation
    follows the Persistence protocol.
    """

    def __init__(
        self, persistence: Persistence, platform_config_dir: Callable
    ):
        self.persistence = persistence or JsonPersistence(
            namespace=RepositoryNamespaces.Timers,
            file_name="session.json",
            settings_dir_path=platform_config_dir(),
            on_read_error=None,
            on_write_error=None,
        )

    def get_all(self) -> list[TimerSet]: ...

    def save(self, data: list[TimerSet]): ...

    @staticmethod
    def _from_list(timers: list[int]) -> TimerSet:
        """Factory for TimerSet from list of timers"""
        ts = TimerSet()
        for timer in timers:
            ts.add(timer)
        return ts
