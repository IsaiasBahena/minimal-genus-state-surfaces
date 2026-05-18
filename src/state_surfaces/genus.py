"""
Utilities for computing the unoriented genus of a state surface.

This module depends only on the original Gauss code and the resulting state
code produced by the smoothing pipeline.
"""

from __future__ import annotations

from typing import Any, List, Sequence


def _as_components(gauss_code: Any) -> List[List[int]]:
    """
    Normalize a Gauss code into list-of-components form.

    Accepted:
      - [1, 2, 3, 1, 2, 3]
      - [[1, 2], [1, 2]]

    Returns
    -------
    list[list[int]]
        Gauss code in component form.
    """

    # Single-component Gauss code.
    if (
        isinstance(gauss_code, list)
        and gauss_code
        and all(isinstance(x, int) for x in gauss_code)
    ):
        return [gauss_code]

    # Multi-component Gauss code.
    if (
        isinstance(gauss_code, list)
        and all(isinstance(comp, list) for comp in gauss_code)
    ):
        return gauss_code

    raise ValueError(
        f"Unsupported Gauss code format for genus computation: {gauss_code!r}"
    )


def _count_crossings(components: Sequence[Sequence[int]]) -> int:
    """
    Count crossings in a Gauss code.

    Each crossing label appears exactly twice across all components, so the
    number of crossings is half the total number of entries.
    """
    total_entries = sum(len(comp) for comp in components)
    return total_entries // 2


def calculate_unoriented_genus(
    original_gauss_code: Any,
    state_code: Sequence[Sequence[int]],
) -> int:
    """
    Compute the unoriented genus of a state surface.

    The genus is computed using:

        g = 1 + c - s

    where:
      - c is the number of crossings in the original Gauss code,
      - s is the number of state circles in the state code.
    """
    components = _as_components(original_gauss_code)

    c = _count_crossings(components)
    s = len(state_code)

    return 1 + c - s
