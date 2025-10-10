"""
This app uses two forms of persistence, each suited to their specific domain.

For settings, user preferences and user defined slideshow parameters JSON is
used as its dict-like hierarchical structure is easy to manipulate and more
than sufficient for most settings/preferences needs where each parameter has a
single value. These are manipulated exclusively in the "settings domain".

For images used during the slideshow and all parameters tied to each image an
SQLite3 database is used. The SQLite3 database provides a very lightweight
indexable solution that allows easy retrieval of all data tied to an image
from any unique identifier or parameter. Manipulated exclusively in the
"resources domain".

This package provides a solution-tied operations API facilitating read and
write with lightweight files.

It holds the following components/services:
  - AppSettings/SlideshowSettings-JsonPersistence:
    - Subclass of JSONPersistance; implements universal API for
      JSON-based file writing and reading. Each one tailored to the
      respective domain's Model dataclass.


  - SQLite3Backend:
    - Subclass of DatabaseBackend; provides API tied to the slideshow images
    for cross resources progress tracking.
"""
