"""
gauss_io.py

Helpers for cleaning / normalizing Gauss codes into a canonical internal format.

This module is intentionally small and conservative:
- It only parses inputs (string or list forms),
- It returns a list of components (list[list[int]]),
- It ensures all crossing labels are positive.

Public API:
    clean_gauss_notation(gauss_code)
"""

from __future__ import annotations

import ast
from typing import Any, List


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def clean_gauss_notation(gauss_code: Any) -> List[List[int]]:
    """
    Normalize a Gauss code into a list of components (list[list[int]])
    with positive crossing labels.

    Accepted formats:
      - String representations of lists
      - Flat list[int] (single component)
      - list[list[int]] (multiple components)

    Returns:
      list[list[int]] with absolute values only
    """

    # ----------------------------------------------------------------------
    # Case 1: string input
    # ----------------------------------------------------------------------
    if isinstance(gauss_code, str):
        try:
            parsed = ast.literal_eval(gauss_code)
        except Exception as e:
            raise ValueError(f"Invalid Gauss code string: {gauss_code}") from e
        return clean_gauss_notation(parsed)

    # ----------------------------------------------------------------------
    # Case 2: list input
    # ----------------------------------------------------------------------
    if isinstance(gauss_code, list):

        # Multiple components
        if gauss_code and all(isinstance(comp, list) for comp in gauss_code):
            return [list(map(abs, comp)) for comp in gauss_code]

        # Single component
        if gauss_code and all(isinstance(x, int) for x in gauss_code):
            return [list(map(abs, gauss_code))]

    raise ValueError(f"Unsupported Gauss code format: {gauss_code}")
