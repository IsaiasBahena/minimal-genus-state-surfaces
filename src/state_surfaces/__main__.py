"""
Package entry point for running:

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
