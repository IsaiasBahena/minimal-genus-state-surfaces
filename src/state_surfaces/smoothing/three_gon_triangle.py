"""
smoothing/three_gon_triangle.py

Triangle (3-gon) smoothing.

Key guarantees
---------------------------
1) We treat the Gauss code as a list of components. A single component input is wrapped.

2) We create two shifted snapshots:
   - code_copy: deep copy used to mutate and build the new Gauss code after smoothing
   - smooth_copy: snapshot saved after shifting FIRST crossings (used only for triangle state circle)

3) We shift in two stages:
   Stage A: shift FIRST triangle crossing (for each of the 3 detected sides) to the front
            -> produce smooth_copy snapshot
   Stage B: shift SECOND triangle crossing to the front (on code_copy)
            -> used to identify triangle pairs for smoothing into new components

4) We "find triangle pairs" by scanning for triangle->triangle along the component,
   storing (start, word, end, comp_idx), with wrap-around slicing.
   NOTE: word/segment is NOT filtered by smoothed crossings.

5) We chain triangle pairs using the same rule:
   - next pair shares the current crossing
   - if shared crossing is on right side, reverse the word

6) We add EXACTLY ONE triangle state circle to smoothed_pairs_copy.

Outputs
-------
Returns:
    (smoothed_gauss_code, updated_smoothed_crossings, updated_smoothed_pairs)

Where:
- smoothed_gauss_code is a list of components (even if it becomes 1 component).
- updated_smoothed_crossings contains the triangle crossings (deduped, sorted like paper).
- updated_smoothed_pairs is the smoothed_pairs list with the triangle state circle appended.
"""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import List, Tuple, Union, Dict, Set, Any


GaussCode = Union[List[int], List[List[int]]]


# ---------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------

def _is_flat_component(code: Any) -> bool:
    return isinstance(code, list) and (len(code) == 0 or all(isinstance(x, int) for x in code))


def _normalize_to_components(gauss_code: GaussCode) -> List[List[int]]:
    """Wrap single component into [component]. Leave multi-component as-is."""
    if _is_flat_component(gauss_code):
        return [gauss_code]  # type: ignore[list-item]
    return gauss_code  # type: ignore[return-value]


def shift_to_start(component: List[int], index: int) -> List[int]:
    """Cyclic shift so that component[index] moves to position 0."""
    if not component:
        return component
    index %= len(component)
    return component[index:] + component[:index]


def _cyclic_slice(component: List[int], i: int, j: int) -> List[int]:
    """
    Return the cyclic segment strictly between i and j:
      segment = comp[i+1:j] if i < j else comp[i+1:] + comp[:j]
    """
    n = len(component)
    if n == 0:
        return []
    i %= n
    j %= n
    if i < j:
        return component[i + 1:j]
    return component[i + 1:] + component[:j]


# ---------------------------------------------------------------------
# Stage: build triangle pairs
# ---------------------------------------------------------------------

def _find_triangle_pairs_in_components(components: List[List[int]], triangle_crossings: Tuple[int, int, int],) -> List[Tuple[int, List[int], int, int]]:
    """
    Find triangle pairs by scanning each component.

    Returns a list of tuples:
        (start_crossing, word_segment, end_crossing, comp_idx)

    Notes:
    - Uses a used_positions set so each triangle crossing occurrence is used at most once
      in this pass.
    - word_segment is the cyclic in-between segment between two triangle crossings.
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

            # scan forward cyclically for the next triangle crossing not already used
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


def _chain_pairs_to_components(pairs: List[Tuple[int, List[int], int, int]]) -> List[List[int]]:
    """
    Chain triangle pairs into smoothed components.

    Each pair is (start, word, end, comp_idx).
    Chaining rule:
      - jump to next pair that contains current crossing
      - if current crossing matches the pair's start: use word forward
      - if matches the pair's end: reverse the word
    """
    smoothed_components: List[List[int]] = []
    visited: Set[int] = set()

    pair_map: Dict[int, List[Tuple[int, Tuple[int, List[int], int, int]]]] = defaultdict(list)
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
    Build exactly one triangle state circle from smooth_copy.

    We:
      1) find triangle_smoothed_pairs (same scan logic as triangle_pairs)
      2) build a pair_map keyed by endpoints
      3) chain starting from the first unvisited pair
      4) append ONE state circle and stop
    """
    tri_pairs = _find_triangle_pairs_in_components(smooth_copy, triangle_crossings)

    # Convert to "smoothed-pair" format: (start, segment, end, comp_idx)
    triangle_smoothed_pairs = tri_pairs

    # Chain into a single state circle
    visited: Set[int] = set()
    pair_map: Dict[int, List[Tuple[int, Tuple[int, List[int], int, int]]]] = defaultdict(list)
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

    # Fallback (should not happen if 3-gon detection was correct)
    return tuple(triangle_crossings)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def smooth_3_gon_triangle(gauss_code: GaussCode, triangle_crossings: Tuple[int, int, int], smoothed_crossings: List[int], smoothed_pairs: List[Tuple[int, ...]], c1: int, i1: int, j1: int, c2: int, i2: int, j2: int, c3: int, i3: int, j3: int,) -> Tuple[List[List[int]], List[int], List[Tuple[int, ...]]]:
    """
    Triangle smoothing branch.

    Parameters
    ----------
    gauss_code:
        list[int] (single component) OR list[list[int]] (multi-component).
    triangle_crossings:
        (a,b,c) crossings for the detected 3-gon.
    smoothed_crossings:
        existing list of smoothed crossings.
    smoothed_pairs:
        existing list of state circles (tuples). We append 1 triangle state circle.
    c1,i1,j1,...:
        the component indices and endpoint indices returned by identify_3_gon.
        These specify the 3 sides (pairs) used to decide which crossings to shift.

    Returns
    -------
    (smoothed_gauss_code_components, updated_smoothed_crossings, updated_smoothed_pairs)
    """
    smoothed_pairs_copy = copy.deepcopy(smoothed_pairs)

    components = _normalize_to_components(gauss_code)
    code_copy = copy.deepcopy(components)

    # ------------------------------------------------------------
    # Step 2: shift first triangle crossing of each pair to the front
    # ------------------------------------------------------------
    shift_map: Dict[int, Tuple[int, Tuple[int, int]]] = {}
    for comp_idx, start_idx, end_idx in [(c1, i1, j1), (c2, i2, j2), (c3, i3, j3)]:
        # keeps the smallest start_idx per component if repeated
        if (comp_idx not in shift_map) or (start_idx < shift_map[comp_idx][0]):
            shift_map[comp_idx] = (start_idx, (start_idx, end_idx))

    for comp_idx, (shift_idx, _) in shift_map.items():
        code_copy[comp_idx] = shift_to_start(code_copy[comp_idx], shift_idx)

    # Step 2.5: snapshot after shifting FIRST crossings
    smooth_copy = copy.deepcopy(code_copy)

    # ------------------------------------------------------------
    # Step 3: shift the second triangle crossing of each pair to the front
    # ------------------------------------------------------------
    # first_crossing/second_crossing, then finds second_crossing in code_copy and shifts.
    for comp_idx, (_shift_idx, (i, j)) in shift_map.items():
        # Use ORIGINAL components (not shifted) to pick the "second crossing"
        original_comp = components[comp_idx]
        second_crossing = original_comp[j]

        try:
            second_index = code_copy[comp_idx].index(second_crossing)
            code_copy[comp_idx] = shift_to_start(code_copy[comp_idx], second_index)
        except ValueError:
            # continue safely
            pass

    # ------------------------------------------------------------
    # Step 4 + 5: identify triangle pairs in code_copy and chain them
    # ------------------------------------------------------------
    triangle_pairs = _find_triangle_pairs_in_components(code_copy, triangle_crossings)
    smoothed_components = _chain_pairs_to_components(triangle_pairs)

    # ------------------------------------------------------------
    # Step 6 + 7: build triangle state circle from smooth_copy
    # ------------------------------------------------------------
    state_circle = _build_triangle_state_circle_from_smooth_copy(smooth_copy, triangle_crossings)
    smoothed_pairs_copy.append(tuple(state_circle))

    # ------------------------------------------------------------
    # Step 8: retain unaffected components from ORIGINAL gauss_code
    # ------------------------------------------------------------
    affected = {c1, c2, c3}
    for idx, comp in enumerate(components):
        if idx not in affected:
            smoothed_components.append(comp)

    # ------------------------------------------------------------
    # Step 9: update smoothed crossings with triangle endpoints
    # ------------------------------------------------------------
    for start, _word, end, _comp_idx in triangle_pairs:
        if start not in smoothed_crossings:
            smoothed_crossings.append(start)
        if end not in smoothed_crossings:
            smoothed_crossings.append(end)

    smoothed_crossings = sorted(smoothed_crossings)

    return smoothed_components, smoothed_crossings, smoothed_pairs_copy
