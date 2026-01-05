"""
dt_to_gauss.py

Convert a (multi-component) Dowker–Thistlethwaite (DT) code to a (multi-component)
Gauss code in the format expected by this package.

DT input format
---------------
A DT code is a list of components; each component is a list of integers:
    [[4, 6, 2]]                 # knot (1 component)
    [[6, 10], [8, 2, 4]]        # link (2 components)

This converter accepts negative entries but uses absolute values.

Gauss output format
-------------------
Returns list[list[int]] where each component is a cyclic Gauss word:
    [[1, 2, 3, 1, 2, 3]]
    [[1, 2, 3, 4], [5, 1, 2, 5, 4, 3]]

Notes
-----
- Build "pairs" linking odd index labels (2k+1) to DT entries
- Place each pair twice in a pre-code array
- Sort pairs lexicographically, then label each occurrence by (sorted) pair index + 1
"""

from __future__ import annotations

from typing import Optional, Tuple, List

import ast
import json


DTCode = List[List[int]]
GaussCode = List[List[int]]


def _normalize_dt(dt: object) -> DTCode:
    """
    Normalize DT input into list[list[int]] using absolute integer values.

    Accepts:
      - list[int] as a single-component DT code
      - list[list[int]] as a multi-component DT code
    """

    if isinstance(dt, str):
        s = dt.strip()
        if not s:
            raise ValueError("DT code string is empty.")
        try:
            dt = json.loads(s)
        except json.JSONDecodeError:
            try:
                dt = ast.literal_eval(s)
            except (ValueError, SyntaxError) as e:
                raise ValueError("DT code string could not be parsed as JSON or Python literal.") from e

    if isinstance(dt, (list, tuple)) and dt and all(isinstance(x, int) for x in dt):
        return [[abs(int(x)) for x in dt]]

    if isinstance(dt, (list, tuple)) and all(isinstance(comp, (list, tuple)) for comp in dt):
        out: DTCode = []
        for comp in dt:
            if not all(isinstance(x, int) for x in comp):
                raise ValueError("DT code components must contain only integers.")
            out.append([abs(int(x)) for x in comp])
        return out

    if dt == []:
        return []

    raise ValueError("DT code must be a list[int] or list[list[int]].")


def dt_to_gauss(dt: object) -> GaussCode:
    """
    Convert a DT code to a Gauss code (multi-component).

    Parameters
    ----------
    dt:
        DT code as list[int] (single component) or list[list[int]] (multi-component).
        Negative values are allowed; absolute values are used.

    Returns
    -------
    GaussCode
        A list of components, each a list of positive crossing labels.

    Raises
    ------
    ValueError
        If the DT code is empty in a way that cannot be interpreted, or if the
        code contains invalid entries.
    """
    dt_list = _normalize_dt(dt)
    if not dt_list:
        return []

    # Total number of DT entries across all components
    total_pairs = sum(len(comp) for comp in dt_list)
    if total_pairs == 0:
        return [[] for _ in dt_list]

    # Allocates a linear "pre-code" and "new-code"
    # of length 2 * total_pairs, then slices it into components.
    linear_len = 2 * total_pairs
    pre_code: List[Optional[Tuple[int, int]]] = [None] * linear_len
    new_code: List[int] = [0] * linear_len
    pairs: List[Tuple[int, int]] = []

    # Fill pre_code by placing each pair twice: at position (2k) and (DT-1).
    k = 0
    for comp in dt_list:
        for entry in comp:
            if entry <= 0:
                raise ValueError(f"DT entries must be nonzero positive integers; got {entry}.")
            # Classic DT codes are even; we don't strictly enforce evenness,
            # but we *do* require the index to fit in the allocated array.
            pos_odd = 2 * k          # 0-based position for odd label (2k+1)
            pos_dt = entry - 1       # DT entry is 1-based

            if pos_dt < 0 or pos_dt >= linear_len:
                raise ValueError(
                    f"DT entry {entry} is out of bounds for a DT code with {total_pairs} pairs "
                    f"(expected entries in 1..{linear_len})."
                )

            pair = (min(2 * k + 1, entry), max(2 * k + 1, entry))
            pre_code[pos_odd] = pair
            pre_code[pos_dt] = pair
            pairs.append(pair)
            k += 1

    # Label pairs in sorted order, 1..N (using dict lookup rather than list.index).
    pairs_sorted = sorted(pairs)
    pair_to_label: dict[Tuple[int, int], int] = {}
    for idx, pair in enumerate(pairs_sorted):
        if pair not in pair_to_label:
            pair_to_label[pair] = idx + 1

    for idx, item in enumerate(pre_code):
        if item is None:
            raise ValueError(
                "DT→Gauss conversion failed: encountered an unfilled position. "
                "The DT code may be malformed."
            )
        new_code[idx] = pair_to_label[item]

    # Slice linear gauss word back into components (length 2*len(comp) each)
    out: GaussCode = []
    cursor = 0
    for comp in dt_list:
        comp_len = 2 * len(comp)
        out.append(new_code[cursor : cursor + comp_len])
        cursor += comp_len

    return out


__all__ = ["dt_to_gauss", "DTCode", "GaussCode"]
