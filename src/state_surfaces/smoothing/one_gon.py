"""
Identify and smooth 1-gons in Gauss codes.

A 1-gon is detected when the same crossing label appears twice with only
already-smoothed crossings between the two occurrences. Since Gauss codes are
cyclic, the in-between segment may also wrap around the end of a component.
"""

from __future__ import annotations

from typing import List, Optional, Tuple, Union


GaussCode = Union[List[int], List[List[int]]]


def has_multiple_components(gauss_code: GaussCode) -> bool:
    """Return True if the Gauss code has two or more components."""
    return (
        isinstance(gauss_code, list)
        and len(gauss_code) > 1
        and all(isinstance(comp, list) for comp in gauss_code)
    )


def shift_to_start(component: List[int], index: int) -> List[int]:
    """Cyclically rotate a component so that component[index] is first."""
    if not component:
        return []

    index %= len(component)
    return component[index:] + component[:index]


def identify_1_gon(gauss_code: GaussCode, smoothed_crossings: List[int],) -> Tuple[int, Optional[int], Optional[int], Optional[Tuple[int, ...]], bool, GaussCode]:
    """
    Identify a 1-gon in the Gauss code.

    Returns
    -------
    tuple
        (component_idx, start_position, end_position, pair, found, updated_gauss_code)

    Notes
    -----
    If a 1-gon is found, the relevant component is rotated so that the first
    occurrence used for smoothing is at index 0.
    """
    if (
        not has_multiple_components(gauss_code)
        and isinstance(gauss_code, list)
        and gauss_code
        and isinstance(gauss_code[0], list)
    ):
        gauss_code = gauss_code[0]  # type: ignore[index, assignment]

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

                    only_smoothed_between = all(
                        c in smoothed_crossings for c in in_between
                    )
                    only_smoothed_before = all(c in smoothed_crossings for c in before)
                    only_smoothed_after = all(c in smoothed_crossings for c in after)

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

                    # Wraparound 1-gon: the in-between segment crosses the component boundary.
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

            # Wraparound 1-gon: the in-between segment crosses the component boundary.
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
    Smooth a 1-gon whose start has already been shifted to index 0.

    Parameters
    ----------
    gauss_code:
        Gauss code already updated by `identify_1_gon`.
    start_position:
        Kept for compatibility with the smoothing interface.
    end_position:
        Offset of the second occurrence of the 1-gon crossing.
    smoothed_crossings:
        Crossings already smoothed.
    component:
        Component index for multi-component Gauss codes.

    Returns
    -------
    tuple
        (new_gauss_code, updated_smoothed_crossings)
    """
    if has_multiple_components(gauss_code):
        comps: List[List[int]] = gauss_code  # type: ignore[assignment]
        comp = comps[component]

        if not comp:
            return gauss_code, smoothed_crossings

        crossing = comp[0]
        if crossing not in smoothed_crossings:
            smoothed_crossings.append(crossing)

        comps[component] = comp[end_position:]
        return comps, smoothed_crossings

    comp: List[int] = gauss_code  # type: ignore[assignment]

    if not comp:
        return gauss_code, smoothed_crossings

    crossing = comp[0]
    if crossing not in smoothed_crossings:
        smoothed_crossings.append(crossing)

    return comp[end_position:], smoothed_crossings
