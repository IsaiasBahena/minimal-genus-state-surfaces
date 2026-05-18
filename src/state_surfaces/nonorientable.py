"""
Utilities for determining nonorientable surface properties of a state surface.

These functions operate purely on state codes:
    state_code = list[tuple[int, ...]]
"""

from __future__ import annotations

from collections import defaultdict
from typing import List, Tuple


StateCode = List[Tuple[int, ...]]


def is_two_sided(state_code: StateCode) -> bool:
    """
    Determine whether a state surface is two-sided.

    This checks whether the state circles can be partitioned into two
    disjoint sets such that no crossing label appears twice within
    the same partition (i.e., a bipartite condition).

    Returns
    -------
    bool
        True if the surface is two-sided, False otherwise.
    """
    if not state_code:
        return True  # trivial case

    bucket_a = []
    bucket_b = []
    remaining = list(state_code)

    # Start with first circle in bucket A
    first = remaining.pop(0)
    bucket_a.append(first)
    assigned = set(first)

    changed = True
    while changed:
        changed = False
        to_remove = []

        for circle in remaining:
            circle_set = set(circle)

            in_a = any(x in assigned for x in circle_set & set(sum(bucket_a, ())))
            in_b = any(x in assigned for x in circle_set & set(sum(bucket_b, ())))

            if in_a and in_b:
                # Conflict detected: the surface cannot be two-sided.
                return False

            if in_a:
                bucket_b.append(circle)
                assigned.update(circle)
                to_remove.append(circle)
                changed = True
            elif in_b:
                bucket_a.append(circle)
                assigned.update(circle)
                to_remove.append(circle)
                changed = True

        for circle in to_remove:
            remaining.remove(circle)

    def has_duplicates(bucket: list[tuple[int, ...]]) -> bool:
        flat = [x for circle in bucket for x in circle]
        return len(flat) != len(set(flat))

    if has_duplicates(bucket_a) or has_duplicates(bucket_b):
        return False

    return True


def is_simple(state_code: StateCode) -> bool:
    """
    Determine whether a state surface is simple.

    A state surface is simple if no unordered pair of crossings appears
    in more than one distinct state circle unless those circles are identical.

    Returns
    -------
    bool
        True if the state surface is simple, False otherwise.
    """
    if not state_code:
        return True

    circle_sets = [set(circle) for circle in state_code]
    pair_to_circles = defaultdict(set)

    for idx, crossings in enumerate(circle_sets):
        crossings = list(crossings)
        for i in range(len(crossings)):
            for j in range(i + 1, len(crossings)):
                pair = frozenset((crossings[i], crossings[j]))
                pair_to_circles[pair].add(idx)

    for pair, indices in pair_to_circles.items():
        if len(indices) > 1:
            base = circle_sets[next(iter(indices))]
            if any(circle_sets[i] != base for i in indices):
                return False

    return True


def calculate_crosscap_number(unoriented_genus: int, state_code: StateCode) -> int:
    """
    Compute the crosscap number from the unoriented genus and state code.

    Rules
    -----
    - If the surface is both simple and two-sided:
        crosscap = genus + 1
    - Otherwise:
        crosscap = genus

    Parameters
    ----------
    unoriented_genus : int
        The unoriented genus of the surface.
    state_code : StateCode
        The computed state code.

    Returns
    -------
    int
        The crosscap number.
    """
    sided = is_two_sided(state_code)
    simple = is_simple(state_code)

    if sided and simple:
        return unoriented_genus + 1

    return unoriented_genus
