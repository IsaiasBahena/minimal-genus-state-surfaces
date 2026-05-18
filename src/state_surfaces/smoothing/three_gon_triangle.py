"""
Triangle smoothing for 3-gons in Gauss codes.

Triangle smoothing produces both an updated Gauss code and exactly one new
state circle. The implementation uses two shifted copies: one to build the
new Gauss code and one to construct the triangle state circle.
"""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple, Union


GaussCode = Union[List[int], List[List[int]]]


def _is_flat_component(code: Any) -> bool:
    """Return True if code is a single Gauss-code component."""
    return (
        isinstance(code, list)
        and (len(code) == 0 or all(isinstance(x, int) for x in code))
    )


def _normalize_to_components(gauss_code: GaussCode) -> List[List[int]]:
    """Wrap a single component into list-of-components form."""
    if _is_flat_component(gauss_code):
        return [gauss_code]  # type: ignore[list-item]

    return gauss_code  # type: ignore[return-value]


def shift_to_start(component: List[int], index: int) -> List[int]:
    """Cyclically rotate a component so that component[index] is first."""
    if not component:
        return component

    index %= len(component)
    return component[index:] + component[:index]


def _cyclic_slice(component: List[int], i: int, j: int) -> List[int]:
    """
    Return the cyclic segment strictly between i and j.
    """
    n = len(component)

    if n == 0:
        return []

    i %= n
    j %= n

    if i < j:
        return component[i + 1 : j]

    return component[i + 1 :] + component[:j]


def _find_triangle_pairs_in_components(components: List[List[int]], triangle_crossings: Tuple[int, int, int],) -> List[Tuple[int, List[int], int, int]]:
    """
    Find triangle pairs by scanning each component.

    Returns
    -------
    list
        Tuples of the form:
            (start_crossing, word_segment, end_crossing, component_index)
    """
    tri_set = set(triangle_crossings)

    triangle_pairs: List[Tuple[int, List[int], int, int]] = []
    used_positions: Set[Tuple[int, int]] = set()

    for comp_idx, comp in enumerate(components):
        n = len(comp)
        i = 0

        while i < n:
            if (comp_idx, i) in used_positions:
                i += 1
                continue

            start = comp[i]

            if start not in tri_set:
                i += 1
                continue

            j = (i + 1) % n
            steps = 1

            while steps < n:
                if (comp_idx, j) in used_positions:
                    j = (j + 1) % n
                    steps += 1
                    continue

                end = comp[j]

                if end in tri_set and j != i:
                    word = _cyclic_slice(comp, i, j)

                    triangle_pairs.append((start, word, end, comp_idx))

                    used_positions.add((comp_idx, i))
                    used_positions.add((comp_idx, j))

                    i = (j + 1) % n
                    break

                j = (j + 1) % n
                steps += 1

            else:
                i += 1

    return triangle_pairs


def _chain_pairs_to_components(pairs: List[Tuple[int, List[int], int, int]],) -> List[List[int]]:
    """
    Chain triangle pairs into smoothed components.

    If the shared crossing is encountered on the right side of the next pair,
    the corresponding word is reversed before being appended.
    """
    smoothed_components: List[List[int]] = []
    visited: Set[int] = set()

    pair_map: Dict[
        int,
        List[Tuple[int, Tuple[int, List[int], int, int]]],
    ] = defaultdict(list)

    for idx, (start, word, end, comp_idx) in enumerate(pairs):
        pair_map[start].append((idx, (start, word, end, comp_idx)))
        pair_map[end].append((idx, (start, word, end, comp_idx)))

    for idx, (start, word, end, comp_idx) in enumerate(pairs):
        if idx in visited:
            continue

        comp_out: List[int] = [start] + list(word)

        visited.add(idx)
        next_crossing = end

        while True:
            found_next = False

            for pair_idx, (a, w, b, _) in pair_map[next_crossing]:
                if pair_idx in visited:
                    continue

                if a == next_crossing:
                    comp_out.append(a)
                    comp_out.extend(w)
                    next_crossing = b

                elif b == next_crossing:
                    comp_out.append(b)
                    comp_out.extend(list(reversed(w)))
                    next_crossing = a

                visited.add(pair_idx)
                found_next = True
                break

            if not found_next:
                break

        smoothed_components.append(comp_out)

    return smoothed_components


def _build_triangle_state_circle_from_smooth_copy(smooth_copy: List[List[int]], triangle_crossings: Tuple[int, int, int],) -> Tuple[int, ...]:
    """
    Build exactly one triangle state circle from the shifted smooth-copy data.
    """
    triangle_smoothed_pairs = _find_triangle_pairs_in_components(
        smooth_copy,
        triangle_crossings,
    )

    visited: Set[int] = set()

    pair_map: Dict[
        int,
        List[Tuple[int, Tuple[int, List[int], int, int]]],
    ] = defaultdict(list)

    for idx, (start, seg, end, comp_idx) in enumerate(triangle_smoothed_pairs):
        pair_map[start].append((idx, (start, seg, end, comp_idx)))
        pair_map[end].append((idx, (start, seg, end, comp_idx)))

    for idx, (start, seg, end, comp_idx) in enumerate(triangle_smoothed_pairs):
        if idx in visited:
            continue

        state: List[int] = [start] + list(seg)

        visited.add(idx)
        next_crossing = end

        while True:
            found = False

            for pair_idx, (a, s, b, _) in pair_map[next_crossing]:
                if pair_idx in visited:
                    continue

                if a == next_crossing:
                    state.append(a)
                    state.extend(s)
                    next_crossing = b

                elif b == next_crossing:
                    state.append(b)
                    state.extend(list(reversed(s)))
                    next_crossing = a

                visited.add(pair_idx)
                found = True
                break

            if not found:
                break

        return tuple(state)

    # Fallback case if no chain is constructed.
    return tuple(triangle_crossings)


def smooth_3_gon_triangle(gauss_code: GaussCode, triangle_crossings: Tuple[int, int, int], smoothed_crossings: List[int], smoothed_pairs: List[Tuple[int, ...]], c1: int, i1: int, j1: int, c2: int, i2: int, j2: int, c3: int, i3: int, j3: int,) -> Tuple[List[List[int]], List[int], List[Tuple[int, ...]]]:
    """
    Perform triangle smoothing on a detected 3-gon.

    Returns
    -------
    tuple
        (
            smoothed_gauss_code,
            updated_smoothed_crossings,
            updated_smoothed_pairs,
        )
    """
    smoothed_pairs_copy = copy.deepcopy(smoothed_pairs)

    components = _normalize_to_components(gauss_code)
    code_copy = copy.deepcopy(components)

    # Shift the first triangle crossing of each detected side to the front.
    shift_map: Dict[int, Tuple[int, Tuple[int, int]]] = {}

    for comp_idx, start_idx, end_idx in [
        (c1, i1, j1),
        (c2, i2, j2),
        (c3, i3, j3),
    ]:
        if (
            comp_idx not in shift_map
            or start_idx < shift_map[comp_idx][0]
        ):
            shift_map[comp_idx] = (start_idx, (start_idx, end_idx))

    for comp_idx, (shift_idx, _) in shift_map.items():
        code_copy[comp_idx] = shift_to_start(
            code_copy[comp_idx],
            shift_idx,
        )

    # Save a snapshot after shifting the first crossings.
    smooth_copy = copy.deepcopy(code_copy)

    # Shift the second triangle crossing of each pair to the front.
    for comp_idx, (_shift_idx, (i, j)) in shift_map.items():
        original_comp = components[comp_idx]
        second_crossing = original_comp[j]

        try:
            second_index = code_copy[comp_idx].index(second_crossing)

            code_copy[comp_idx] = shift_to_start(
                code_copy[comp_idx],
                second_index,
            )

        except ValueError:
            pass

    # Build smoothed components from triangle pairs.
    triangle_pairs = _find_triangle_pairs_in_components(
        code_copy,
        triangle_crossings,
    )

    smoothed_components = _chain_pairs_to_components(triangle_pairs)

    # Build exactly one triangle state circle.
    state_circle = _build_triangle_state_circle_from_smooth_copy(
        smooth_copy,
        triangle_crossings,
    )

    smoothed_pairs_copy.append(tuple(state_circle))

    # Retain unaffected components.
    affected = {c1, c2, c3}

    for idx, comp in enumerate(components):
        if idx not in affected:
            smoothed_components.append(comp)

    # Update smoothed crossings.
    for start, _word, end, _comp_idx in triangle_pairs:
        if start not in smoothed_crossings:
            smoothed_crossings.append(start)

        if end not in smoothed_crossings:
            smoothed_crossings.append(end)

    smoothed_crossings = sorted(smoothed_crossings)

    return (
        smoothed_components,
        smoothed_crossings,
        smoothed_pairs_copy,
    )
