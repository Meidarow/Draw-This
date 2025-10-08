class DatabaseWriterError(Exception):
    pass


class CommitError(DatabaseWriterError):
    """Error when attempting to commit rows to chosen database."""
