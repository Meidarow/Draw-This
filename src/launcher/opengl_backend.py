
"""
OpenGL Backend for Draw-This.

This module defines the function that serves as an interface between the GUI and FEH:
It has a single function:

- start_slideshow:
    Accepts a series of parameters and builds a bash command calling feh with a series
    of flags, according to user preferences.

Usage
-----
This file is imported as a package according to the following:
    import launcher.feh_backend
"""