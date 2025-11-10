class DatabaseError(Exception):
    pass


class PersistenceError(DatabaseError):
    """Error"""


class CommitError(DatabaseError):
    """Error when attempting to commit rows to chosen database."""


class ObjectNotFoundError(DatabaseError):
    """Failed to find object in databse"""
