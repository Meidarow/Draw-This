from pathlib import Path

"""
Simple parsing utility meant for shaders, to be used in the openGL backend in Draw-This.

This module defines the parser and it's functionality.
It has one function:

- parse_shader:
    Takes a single file name or pathlib.Path and returns its contents as a string.

Usage
-----
This file is imported by Viewmodel as a package according to the following:
    from drawthis import shader_parser
"""


def parse_shader(file: str | Path) -> str:
    """Parses content of shader files encoded in utf-8.

    Attributes:
        :params file: File name of the shader file.
    """

    path = Path("/drawthis").expanduser() / "render" / "shaders" / file
    if not path.exists():
        raise FileNotFoundError(f"Shader file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return f.read()
