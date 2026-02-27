"""
smoothing/one_gon.py

Identify and smooth 1-gons (monogons) in Gauss codes.

A "1-gon" is detected when the same crossing label appears twice with ONLY
already-smoothed crossings in between (possibly via wraparound in a cyclic list).

Conventions
-----------
- A Gauss code can be either:
    * single-component: list[int]
    * multi-component:  list[list[int]]

- smoothed_crossings is a list[int] tracking which crossings are already smoothed.

Public API
----------
identify_1_gon(gauss_code, smoothed_crossings)
smooth_1_gon(gauss_code, start_position, end_position, smoothed_crossings, component)
"""

from __future__ import annotations

from typing import List, Tuple, Union, Optional


GaussCode = Union[List[int], List[List[int]]]


def has_multiple_components(gauss_code: GaussCode) -> bool:
    """True iff gauss_code is a list of >=2 components (each a list[int])."""
    return (
        isinstance(gauss_code, list)
        and len(gauss_code) > 1
        and all(isinstance(comp, list) for comp in gauss_code)
    )


def shift_to_start(component: List[int], index: int) -> List[int]:
    """Cyclically rotate component so that component[index] becomes first."""
    if not component:
        return []
    index %= len(component)
    return component[index:] + component[:index]


def identify_1_gon(gauss_code: GaussCode, smoothed_crossings: List[int],) -> Tuple[int, Optional[int], Optional[int], Optional[Tuple[int, ...]], bool, GaussCode]:
    """
    Identify a 1-gon in the Gauss code.

    Returns
    -------
    (component_idx, start_position, end_position, pair, found, updated_gauss_code)

    Notes
    -----
    - For a detected 1-gon, the relevant component is rotated so the first
      occurrence used is at index 0 (start_position = 0 in the return).
    - end_position is returned as an offset in the shifted component: (end - start) % n.
    - pair is the tuple that gets appended to the state code (smoothed_pairs).
    """
    # If a single component is wrapped as [component], unwrap it (matches paper behavior)
    if not has_multiple_components(gauss_code) and isinstance(gauss_code, list) and gauss_code and isinstance(gauss_code[0], list):
        # type: ignore[assignment]
        gauss_code = gauss_code[0]  # type: ignore[index]

    # --- Multi-component case ---
    if has_multiple_components(gauss_code):
        comps: List[List[int]] = gauss_code  # type: ignore[assignment]

        for comp_idx, component in enumerate(comps):
            n = len(component)
            if n == 0:
                continue

            for i in range(n):
                crossing = component[i]
                for j in range(i + 1, n):
                    if component[j] != crossing:
                        continue

                    in_between = component[i + 1 : j]
                    before = component[:i]
                    after = component[j + 1 :]

                    only_smoothed_between = all(c in smoothed_crossings for c in in_between)
                    only_smoothed_before = all(c in smoothed_crossings for c in before)
                    only_smoothed_after = all(c in smoothed_crossings for c in after)

                    # Non-wraparound 1-gon
                    if only_smoothed_between:
                        start_position = i
                        end_position = j
                        pair = (crossing, *in_between)

                        shifted = shift_to_start(component, start_position)
                        updated = comps[:]
                        updated[comp_idx] = shifted

                        return (
                            comp_idx,
                            0,
                            (end_position - start_position) % n,
                            tuple(pair),
                            True,
                            updated,
                        )

                    # Wraparound 1-gon: the "between" segment crosses the end/start boundary
                    if only_smoothed_before and only_smoothed_after:
                        start_position = j
                        end_position = i
                        pair = (crossing, *after, *before)

                        shifted = shift_to_start(component, start_position)
                        updated = comps[:]
                        updated[comp_idx] = shifted

                        return (
                            comp_idx,
                            0,
                            (end_position - start_position) % n,
                            tuple(pair),
                            True,
                            updated,
                        )

        return -1, None, None, None, False, gauss_code

    # --- Single-component case ---
    comp: List[int] = gauss_code  # type: ignore[assignment]
    n = len(comp)
    if n == 0:
        return -1, None, None, None, False, gauss_code

    for i in range(n):
        crossing = comp[i]
        for j in range(i + 1, n):
            if comp[j] != crossing:
                continue

            in_between = comp[i + 1 : j]
            before = comp[:i]
            after = comp[j + 1 :]

            only_smoothed_between = bool(smoothed_crossings) and all(
                c in smoothed_crossings for c in in_between
            )
            only_smoothed_before = bool(smoothed_crossings) and all(
                c in smoothed_crossings for c in before
            )
            only_smoothed_after = bool(smoothed_crossings) and all(
                c in smoothed_crossings for c in after
            )

            if only_smoothed_between:
                start_position = i
                end_position = j
                pair = (crossing, *in_between)

                shifted = shift_to_start(comp, start_position)
                return (
                    -1,
                    0,
                    (end_position - start_position) % n,
                    tuple(pair),
                    True,
                    shifted,
                )

            if only_smoothed_before and only_smoothed_after:
                start_position = j
                end_position = i
                pair = (crossing, *after, *before)

                shifted = shift_to_start(comp, start_position)
                return (
                    -1,
                    0,
                    (end_position - start_position) % n,
                    tuple(pair),
                    True,
                    shifted,
                )

    return -1, None, None, None, False, gauss_code


def smooth_1_gon(gauss_code: GaussCode, start_position: int, end_position: int, smoothed_crossings: List[int], component: int,) -> Tuple[GaussCode, List[int]]:
    """
    Smooth a 1-gon that has already been shifted so its start is at index 0.

    Parameters
    ----------
    gauss_code : GaussCode
        The Gauss code (already updated/shifted by identify_1_gon).
    start_position : int
        Kept for signature compatibility. Expected to be 0 after shifting.
    end_position : int
        Offset index in the shifted component pointing to the second occurrence
        of the 1-gon crossing.
    smoothed_crossings : list[int]
        Updated in-place (and returned) by appending the 1-gon crossing.
    component : int
        Component index if multi-component; ignored for single-component.

    Returns
    -------
    (new_gauss_code, smoothed_crossings)
    """
    # Multi-component
    if has_multiple_components(gauss_code):
        comps: List[List[int]] = gauss_code  # type: ignore[assignment]
        comp = comps[component]
        if not comp:
            return gauss_code, smoothed_crossings

        a = comp[0]  # start is at 0 after shifting
        if a not in smoothed_crossings:
            smoothed_crossings.append(a)

        # Remove the 1-gon (inclusive of both ends): keep everything from end_position onward
        new_component = comp[end_position:]
        comps[component] = new_component
        return comps, smoothed_crossings

    # Single-component
    comp: List[int] = gauss_code  # type: ignore[assignment]
    if not comp:
        return gauss_code, smoothed_crossings

    a = comp[0]
    if a not in smoothed_crossings:
        smoothed_crossings.append(a)

    new_gauss_code = comp[end_position:]
    return new_gauss_code, smoothed_crossings
