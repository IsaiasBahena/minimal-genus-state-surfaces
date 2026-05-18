"""
Helpers for normalizing Gauss codes into a canonical internal format.

This module accepts string or list representations of Gauss codes and converts
them into the standard internal representation used throughout the package:
list[list[int]] with positive crossing labels.
"""

from __future__ import annotations

import ast
from typing import Any, List


def clean_gauss_notation(gauss_code: Any) -> List[List[int]]:
    """
    Normalize a Gauss code into list[list[int]] form with positive labels.

    Accepted formats:
      - String representations of lists
      - list[int] for a single component
      - list[list[int]] for multiple components

    Returns
    -------
    list[list[int]]
        Canonical Gauss code representation using absolute values.
    """

    # Parse string input recursively.
    if isinstance(gauss_code, str):
        try:
            parsed = ast.literal_eval(gauss_code)
        except Exception as e:
            raise ValueError(f"Invalid Gauss code string: {gauss_code}") from e

        return clean_gauss_notation(parsed)

    # Multi-component Gauss code.
    if isinstance(gauss_code, list):
        if gauss_code and all(isinstance(comp, list) for comp in gauss_code):
            return [list(map(abs, comp)) for comp in gauss_code]

        # Single-component Gauss code.
        if gauss_code and all(isinstance(x, int) for x in gauss_code):
            return [list(map(abs, gauss_code))]

    raise ValueError(f"Unsupported Gauss code format: {gauss_code}")
