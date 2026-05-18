"""
Detection logic for 3-gons in Gauss codes.

This module only identifies 3-gons. The two smoothing branches are implemented
separately in `three_gon_triangle.py` and `three_gon_anti_triangle.py`.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple


def _get_in_between(component: List[int], i: int, j: int) -> List[int]:
    """Return the cyclic segment strictly between indices i and j."""
    n = len(component)

    if i < j:
        return component[i + 1 : j]

    return component[i + 1 :] + component[:j]


def identify_3_gon(gauss_code: Any, smoothed_crossings: List[int],) -> Tuple[Optional[Tuple[int, int, int]], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], bool,]:
    """
    Identify a 3-gon in a Gauss code.

    A valid 3-gon is determined by three valid sides of the form
    (a, b), (b, c), and (a, c), where all crossings between side endpoints
    have already been smoothed.

    Returns
    -------
    tuple
        Triangle crossings, side component/index data, and a boolean flag.
    """
    if all(isinstance(x, int) for x in gauss_code):
        gauss_code = [gauss_code]

    found_3_gons = set()
    pairs = []

    # Collect all valid sides whose in-between entries are already smoothed.
    for comp_idx, component in enumerate(gauss_code):
        n = len(component)

        for i in range(n):
            a = component[i]

            if a in smoothed_crossings:
                continue

            for j in range(1, n):
                end_idx = (i + j) % n
                b = component[end_idx]

                if b == a or b in smoothed_crossings:
                    continue

                in_between = _get_in_between(component, i, end_idx)

                if any(c not in smoothed_crossings for c in in_between):
                    continue

                pairs.append(((a, b), comp_idx, i, end_idx))

    # Search for three sides forming (a, b), (b, c), and (a, c).
    for pair1, c1, i1, j1 in pairs:
        a, b = pair1

        for pair2, c2, i2, j2 in pairs:
            if (c2, i2) == (c1, i1):
                continue

            if b not in pair2:
                continue

            c = pair2[1] if pair2[0] == b else pair2[0]

            if c == a or c in smoothed_crossings:
                continue

            for pair3, c3, i3, j3 in pairs:
                if (c3, i3) in [(c1, i1), (c2, i2)]:
                    continue

                if a not in pair3 or c not in pair3:
                    continue

                in_between_1 = _get_in_between(gauss_code[c1], i1, j1)
                in_between_2 = _get_in_between(gauss_code[c2], i2, j2)
                in_between_3 = _get_in_between(gauss_code[c3], i3, j3)

                if any(
                    crossing not in smoothed_crossings
                    for crossing in in_between_1 + in_between_2 + in_between_3
                ):
                    continue

                standardized = tuple(sorted([a, b, c]))

                if standardized not in found_3_gons:
                    found_3_gons.add(standardized)
                    return (a, b, c), c1, i1, j1, c2, i2, j2, c3, i3, j3, True

    return None, None, None, None, None, None, None, None, None, None, False
