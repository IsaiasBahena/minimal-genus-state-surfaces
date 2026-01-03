"""
__main__.py

Module entry point for the state_surfaces package.

Allows the package to be executed with:
    python -m state_surfaces
"""

from __future__ import annotations

import sys

from .cli import main


def _entry() -> None:
    """Entry point wrapper for `python -m state_surfaces`."""
    sys.exit(main())


if __name__ == "__main__":
    _entry()
