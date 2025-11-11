"""
Behavioral contract: removal ops must always...

Assumptions:
  - Removal criteria is a field in a row, thus contained in an ImageRow
  - Provided data is iterable or singular

Expected behavior:
EB1 Every entry that matches removal criteria should be removed DB
    (regardless of other fields)
EB2 All entries that have not been removed are unaltered DB
EB3 Row IDs are reordered to maintain exact order of remaining rows DB

Acceptance criteria:
AC1 Database contains no matching entries after removal DB
AC2 Remaining entries are unaltered (except for primary ID) DB
AC3 Partial matches are not altered DB
AC4 Each removal query (by provided criteria) is atomic REPO
"""

"""
    Behavioral contract: Load operations must always...

    Assumptions:
      - Data consistency is guaranteed within a single load operation
        (no mid-read mutations)
      - Row order is preserved for any accepted criterion

    Expected behavior:
    EB1 All entries in the database are returned REPO
    EB2 Entries are returned sorted by the provided criterion REPO
    EB3 Entries can be deterministically indexed by that criterion, and
        the order must match the load order HANDLER

    Acceptance criteria:
    AC1 All entries are provided, sorted according to a deterministic 
    criterion REPO+HANDLER
    AC2 Ordering and indexing are reproducible given the same criterion 
    REPO+HANDLER
    """

"""
    Behavioral contract: Insert ops must always...

    Assumptions:
      - Every row is a valid ImageRow instance
      - Provided data is a flat iterable (including single rows)

    Compromises:
      - Uniqueness defined as ≥2 of {path, inode+dev, size} matching

    Expected behavior:
    EB1 Files with identical path & size → skipped HANDLER
    EB2 Files with identical inode+dev & size → skipped HANDLER
    EB3 Files with identical path & inode+dev → skipped HANDLER
    EB4 Files with fewer than 2 matches → inserted as unique HANDLER

    Acceptance criteria:
    AC1 insert_rows() returns count of unique inserts DB+REPO
    AC2 Database contains no duplicate paths after insertion DB
    AC3 Insertion commits atomically (WAL checkpoint visible) REPO
    """
"""
Behavioral contract for SQLite3Backend:

Core behaviors:
  - Inserts rows in provided batch via insert_rows() in single transaction
  - Removes rows for provided parent paths in single transaction
  - Maintains schema integrity and migrations*
    *Additive migrations only

Data guarantees:
  - Deterministic-random ordering of rows across reads* by randid
  - Seen status persists correctly on close
  - Writes and reads are atomic and committed
  - Provides metrics of inserted/removed rows
    *Writes overwrite the randid changing order

Error handling:
  - Handles recoverable errors (locked DB, invalid inputs) gracefully
"""
