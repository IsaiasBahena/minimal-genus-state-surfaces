"""
three_gon_anti_triangle.py

Anti-triangle (3-gon) smoothing for Gauss codes.

This implementation:
- Supports multi-component Gauss codes (single components are wrapped).
- Shifts each involved component so the first triangle crossing appears at the front.
- Constructs anti-triangle pairs subject to the usage-count-4 constraint.
- Labels pairs alternately as s/w and chains them with the same ordering rules.
- Enforces the consecutive same-component constraint.
- Does NOT add a state circle (anti-triangle smoothing produces no state pair).
"""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import List, Tuple, Dict, Any


def _is_list_of_ints(x: Any) -> bool:
    return isinstance(x, list) and all(isinstance(v, int) for v in x)


def _ensure_components(gauss_code: Any) -> List[List[int]]:
    """Wrap a single component as [component] if needed."""
    if _is_list_of_ints(gauss_code):
        return [gauss_code]
    return gauss_code


def shift_to_start(component: List[int], index: int) -> List[int]:
    """Cyclically shift a component so component[index] is first."""
    if not component:
        return component
    index %= len(component)
    return component[index:] + component[:index]


def _forward_dist(cur: int, idx: int, total: int) -> int:
    d = (idx - cur) % total
    return d if d != 0 else total


def _backward_dist(cur: int, idx: int, total: int) -> int:
    d = (cur - idx) % total
    return d if d != 0 else total


def smooth_3_gon_anti_triangle(gauss_code: Any, triangle_crossings: Tuple[int, int, int], smoothed_crossings: List[int], c1: int, i1: int, j1: int, c2: int, i2: int, j2: int, c3: int, i3: int, j3: int,) -> Tuple[List[List[int]], List[int]]:
    """
    Perform anti-triangle smoothing on a Gauss code.

    Parameters
    ----------
    gauss_code : list[list[int]] or list[int]
        The Gauss code to smooth.
    triangle_crossings : tuple(int, int, int)
        The three crossings forming the 3-gon.
    smoothed_crossings : list[int]
        Crossings already smoothed.
    (c1,i1,j1), (c2,i2,j2), (c3,i3,j3)
        Component and index data returned by identify_3_gon.

    Returns
    -------
    new_gauss_code : list[list[int]]
        The Gauss code after anti-triangle smoothing.
    smoothed_crossings : list[int]
        Updated smoothed crossings.
    """
    gauss_code = _ensure_components(gauss_code)
    code_copy = copy.deepcopy(gauss_code)

    # --- Step 1: shift relevant components ---
    shift_map: Dict[int, Tuple[int, Tuple[int, int]]] = {}
    for comp_idx, start_idx, end_idx in [(c1, i1, j1), (c2, i2, j2), (c3, i3, j3)]:
        if comp_idx not in shift_map or start_idx < shift_map[comp_idx][0]:
            shift_map[comp_idx] = (start_idx, (start_idx, end_idx))

    for comp_idx, (shift_idx, _) in shift_map.items():
        code_copy[comp_idx] = shift_to_start(code_copy[comp_idx], shift_idx)

    # --- Step 2: build anti-triangle pairs ---
    anti_triangle_pairs = []
    usage_count = defaultdict(int)
    triangle_set = set(triangle_crossings)

    for comp_idx in shift_map:
        comp = code_copy[comp_idx]
        n = len(comp)

        for i in range(n):
            start = comp[i]
            if start not in triangle_set or usage_count[start] >= 4:
                continue

            for step in range(1, n):
                j = (i + step) % n
                end = comp[j]
                if end in triangle_set and usage_count[end] < 4 and i != j:
                    if i < j:
                        segment = comp[i + 1:j]
                    else:
                        segment = comp[i + 1:] + comp[:j]

                    anti_triangle_pairs.append((start, segment, end, comp_idx))
                    usage_count[start] += 1
                    usage_count[end] += 1
                    break

    # --- Step 3: label pairs alternately s/w ---
    labeled_pairs = []
    for idx, pair in enumerate(anti_triangle_pairs):
        label = f"{idx + 1}{'s' if idx % 2 == 0 else 'w'}"
        labeled_pairs.append((label, pair))

    # --- Step 4: same-component neighbor ring ---
    comp_to_indices = defaultdict(list)
    for idx, (_, (_, _, _, comp_idx)) in enumerate(labeled_pairs):
        comp_to_indices[comp_idx].append(idx)

    samecomp_neighbors = {}
    for comp, idxs in comp_to_indices.items():
        idxs.sort()
        m = len(idxs)
        for k, cur in enumerate(idxs):
            samecomp_neighbors[cur] = (idxs[(k - 1) % m], idxs[(k + 1) % m])

    def violates_consecutive(prev_idx, cand_idx, cand_side, scan_dir):
        if prev_idx not in samecomp_neighbors:
            return False
        prev_in, next_in = samecomp_neighbors[prev_idx]
        if scan_dir == "forward":
            return cand_idx == next_in and cand_side == "start"
        return cand_idx == prev_in and cand_side == "end"

    # --- Step 5: chain pairs into components ---
    smoothed_components = []
    used_indices = set()
    total_pairs = len(labeled_pairs)

    while len(used_indices) < total_pairs:
        # Seed a new component with the first unused pair
        for idx, (label, (start, segment, end, _)) in enumerate(labeled_pairs):
            if idx not in used_indices:
                component = [start] + segment
                current_crossing = end
                current_idx = idx
                used_indices.add(idx)
                expect_word = label.endswith("s")
                last_side = "end"
                break
        else:
            break

        scan_dir = "forward"

        while True:
            found = False
            candidates = []

            for idx, (label, (s, segment, e, comp_of_pair)) in enumerate(labeled_pairs):
                if idx in used_indices:
                    continue
                if label.endswith("s") == expect_word:
                    continue

                if s != e:
                    if current_crossing == s:
                        cand_side = "start"
                        write_dir = "forward"
                    elif current_crossing == e:
                        cand_side = "end"
                        write_dir = "reverse"
                    else:
                        continue

                    candidates.append({
                        "idx": idx,
                        "label": label,
                        "s": s,
                        "e": e,
                        "seg": segment,
                        "cand_side": cand_side,
                        "write_dir": write_dir,
                        "comp": comp_of_pair,
                    })

                else:
                    if current_crossing != s:
                        continue

                    candidates.append({
                        "idx": idx,
                        "label": label,
                        "s": s,
                        "e": e,
                        "seg": segment,
                        "cand_side": "start",
                        "write_dir": "forward",
                        "comp": comp_of_pair,
                    })
                    candidates.append({
                        "idx": idx,
                        "label": label,
                        "s": s,
                        "e": e,
                        "seg": segment,
                        "cand_side": "end",
                        "write_dir": "reverse",
                        "comp": comp_of_pair,
                    })

            if not candidates:
                break

            if last_side == "end":
                for cand in candidates:
                    cand["dist"] = _forward_dist(current_idx, cand["idx"], total_pairs)
                candidates.sort(key=lambda cand: (cand["dist"], cand["idx"]))

            elif last_side == "start":
                for cand in candidates:
                    cand["dist"] = _backward_dist(current_idx, cand["idx"], total_pairs)
                candidates.sort(key=lambda cand: (cand["dist"], (-cand["idx"]) % total_pairs))

            else:
                for cand in candidates:
                    cand["dist"] = _forward_dist(current_idx, cand["idx"], total_pairs)
                candidates.sort(key=lambda cand: (cand["dist"], cand["idx"]))

            prev_comp = labeled_pairs[current_idx][1][3]

            for cand in candidates:
                idx = cand["idx"]
                s = cand["s"]
                e = cand["e"]
                segment = cand["seg"]
                cand_side = cand["cand_side"]
                write_dir = cand["write_dir"]
                cand_comp = cand["comp"]

                same_component = cand_comp == prev_comp

                if same_component and violates_consecutive(
                    current_idx,
                    idx,
                    cand_side,
                    scan_dir,
                ):
                    continue

                if write_dir == "forward":
                    component.append(s)
                    component.extend(segment)
                    current_crossing = e
                    last_side = "end"
                    scan_dir = "forward"

                else:
                    component.append(e)
                    component.extend(reversed(segment))
                    current_crossing = s
                    last_side = "start"
                    scan_dir = "backward"

                used_indices.add(idx)
                current_idx = idx
                expect_word = not expect_word
                found = True
                break

            if not found:
                break

        smoothed_components.append(component)

    # --- Step 6: add unaffected components ---
    affected = {c1, c2, c3}
    for idx, comp in enumerate(gauss_code):
        if idx not in affected:
            smoothed_components.append(comp)

    # --- Step 7: update smoothed crossings ---
    for c in triangle_crossings:
        if c not in smoothed_crossings:
            smoothed_crossings.append(c)

    return smoothed_components, smoothed_crossings
