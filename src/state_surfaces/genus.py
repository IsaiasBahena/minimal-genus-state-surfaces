"""
genus.py


Utilities for computing the (unoriented) genus of a Kauffman state surface.

This module is intentionally small and stable: it only depends on the
original Gauss code and the computed state code.


Public API:
    calculate_unoriented_genus(original_gauss_code, state_code)
"""

from __future__ import annotations

from typing import Any, List, Sequence


# ---------------------------------------------------------------------------
# Small local helpers
# ---------------------------------------------------------------------------


def _as_components(gauss_code: Any) -> List[List[int]]:
    """
    Normalize a Gauss code into list-of-components form.

    Accepted:
        - [1, 2, 3, 1, 2, 3]          (single component)
        - [[1, 2], [1, 2]]            (multiple components)

    Returns:
        list[list[int]] (no parsing of strings happens here)
    """

    # Single component: wrap
    if isinstance(gauss_code, list) and gauss_code and all(isinstance(x, int) for x in gauss_code):
        return [gauss_code]

    # Multi-component: already list-of-lists
    if isinstance(gauss_code, list) and all(isinstance(comp, list) for comp in gauss_code):
        return gauss_code

    raise ValueError(f"Unsupported Gauss code format for genus computation: {gauss_code!r}")


def _count_crossings(components: Sequence[Sequence[int]]) -> int:
    """
    Count crossings c from a Gauss code in component form.

    Each crossing label appears exactly twice across the whole Gauss code,
    so: c = (total number of entries) // 2.
    """

    total_entries = sum(len(comp) for comp in components)
    return total_entries // 2


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_unoriented_genus(original_gauss_code: Any, state_code: Sequence[Sequence[int]],) -> int:
    """
    Calculate the unoriented genus using the formula:

        g = 1 + c - s

    where:
        - c = number of crossings in the original Gauss code
        - s = number of state circles in the state code

    Notes:
        - This matches the paper implementation.
        - We treat s = len(state_code), since each element of state_code is one state circle.
    """

    components = _as_components(original_gauss_code)

    c = _count_crossings(components)
    s = len(state_code)

    return 1 + c - s
