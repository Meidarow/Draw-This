from uuid import UUID

from iteradraw.domain.models.folder import FolderSet
from iteradraw.infrastructure.persistence.sqlite3_domain_database import (
    SQLite3DomainDatabase,
)


class FolderRepository:
    """
    Repository for FolderSet domain objects.

    Facilitates persistence operations for the FolderSet model by
    abstracting backend implementations and providing (de-)serialization
    methods. Allows for backend injection, as long as implementation follows
    the Persistence protocol.

    Handles only FolderSets since an individual Folder is not meant to exist
    outside a folder set.
    """

    def __init__(self, persistence: SQLite3DomainDatabase):
        self.persistence = persistence

    def get(self, folderset_id: UUID) -> FolderSet:
        folderset_id_str = str(folderset_id)
        return self.persistence.get_folderset(name=folderset_id_str)

    def get_all(self) -> list[FolderSet]:
        return self.persistence.get_all_foldersets()

    def save(self, folderset: FolderSet):
        self.persistence.save_folderset(folderset=folderset)

    def remove(self, folderset_id: UUID):
        folderset_id_str = str(folderset_id)
        self.persistence.delete_folderset(name=folderset_id_str)
