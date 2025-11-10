# """ TODO
# Logger _.
#
# This module defines the logger and it's functionality.
# It has one class:
#
# - Logger:
# Rotates a file based on file size, logs to stream also.
#
# Usage
# -----
# This file is imported by Viewmodel as a package according to the following:
#     from drawthis import Logger
# """
#
# logger = logging.getLogger("drawthis")
# logger.setLevel(logging.DEBUG)
#
# file_handler = RotatingFileHandler(LOG_FOLDER, encoding="utf-8")
# file_handler.setLevel(level=logging.DEBUG)
# file_handler.setFormatter(
#     fmt=logging.Formatter(
#         "%(asctime)s [%(levelname)s] (%(name)s): (%(message)s)"
#     )
# )
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(level=logging.WARNING)
# stream_handler.setFormatter(
#     fmt=logging.Formatter("[%(levelname)s] (%(name)s): (%(message)s)")
# )
#
# if not logger.handlers:
#     logger.addHandler(file_handler)
#     logger.addHandler(stream_handler)

