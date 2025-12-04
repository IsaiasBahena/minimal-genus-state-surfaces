"""
pipeline.py


High-level pipeline for computing:
- Kauffman state codes (via 1-gon, 2-gon, and 3-gon smoothings),
- unoriented genus,
- crosscap number,
starting from either Gauss codes or DT codes.


Public API:
    process_gauss_code(gauss_code)
    compute_invariants(gauss_code, state_code)
    run_pipeline(gauss_code=None, dt_code=None)
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Sequence, Tuple

from .gauss_io import clean_gauss_notation
from .dt_to_gauss import dt_to_gauss
from .genus import calculate_unoriented_genus
from .nonorientable import calculate_crosscap_number, is_simple, is_two_sided
from .smoothing.one_gon import identify_1_gon, smooth_1_gon
from .smoothing.two_gon import identify_2_gon, smooth_2_gon
from .smoothing.three_gon_triangle import identify_3_gon, smooth_3_gon_triangle
from .smoothing.three_gon_anti_triangle import smooth_3_gon_anti_triangle


# ---------------------------------------------------------------------------
# Small local helpers
# ---------------------------------------------------------------------------


def _has_multiple_components(gauss_code: Any) -> bool:
    """Return True iff gauss_code is a list of >=2 component-lists."""
    
    return (
        isinstance(gauss_code, list)
        and len(gauss_code) > 1
        and all(isinstance(comp, list) for comp in gauss_code)
    )


def _is_list_of_components(gauss_code: Any) -> bool:
    """Return True iff gauss_code is a list whose elements are component-lists."""
    
    return (
        isinstance(gauss_code, list)
        and all(isinstance(comp, list) for comp in gauss_code)
    )


def _normalize_gauss_code(gauss_code: Any) -> List[List[int]]:
    """
    Normalize input into a list of components (list[list[int]]) with positive labels.


    Accepted formats:
    - [1, 2, 3, 4, 1, 2, 3, 4]      (single component)
    - [[1, 2, 3, 1], [2, 3, 4, 4]]  (multiple components)
    - Gauss notation string         (handled via clean_gauss_notation)
    """
    
    if isinstance(gauss_code, str):
        return clean_gauss_notation(gauss_code)
    

    if isinstance(gauss_code, list):
        # list of components
        if gauss_code and all(isinstance(comp, list) for comp in gauss_code):
            return [list(map(abs,comp)) for comp in gauss_code]
        # single component
        if gauss_code and all(isinstance(x, int) for x in gauss_code):
            return [list(map(abs,gauss_code))]


    # Fallback: try to parse via clean_gauss_notation
    return clean_gauss_notation(gauss_code)


# ---------------------------------------------------------------------------
# Core recursive smoothing logic
# ---------------------------------------------------------------------------


def _process_branch(gauss_code: Any, smoothed_crossings: List[int], smoothed_pairs: List[Tuple[int, ...]], original_gauss_code: Any,) -> List[Tuple[int, ...]]:
    """
    Recursively smooth the Gauss code along one branch of the algorithm
    (i.e., a fixed choice of triangle vs anti-triangle smoothing each time).


    Returns:
        state_code: a list of tuples, each tuple representing a state circle.
    """

    smoothed_crossings = copy.deepcopy(smoothed_crossings)
    smoothed_pairs = copy.deepcopy(smoothed_pairs)


    # If we accidentally get [[...]] with a single component, unwrap to [...]
    if isinstance(gauss_code, list) and len(gauss_code) == 1 and not _has_multiple_components(gauss_code):
        gauss_code = gauss_code[0]
    

    while True:
        something_smoothed = False # track if we changed anything in this iteration


        # ------------------------------------------------------------------
        # Case 1: multiple components
        # ------------------------------------------------------------------
        if _has_multiple_components(gauss_code):
            # 1-gon in any component
            (
                component_idx,
                start_position,
                end_position,
                pair,
                is_true_1_gon,
                updated_gauss_code,
            ) = identify_1_gon(gauss_code, smoothed_crossings)


            if is_true_1_gon:
                smoothed_pairs.append(pair)
                gauss_code, smoothed_crossings = smooth_1_gon(
                    updated_gauss_code,
                    start_position,
                    end_position,
                    smoothed_crossings,
                    component_idx,
                )
                something_smoothed = True
                continue


            # 2-gon in any component(s)
            (
                case,
                a1,
                b1,
                a2,
                b2,
                pair,
                is_true_2_gon,
                is_2_gon_multiple_component,
                component_idx1,
                component_idx2,
                updated_gauss_code,
            ) = identify_2_gon(gauss_code, smoothed_crossings)


            if is_true_2_gon:
                gauss_code, smoothed_crossings, new_smoothed_pairs = smooth_2_gon(
                    updated_gauss_code,
                    case,
                    a1,
                    b1,
                    a2,
                    b2,
                    smoothed_crossings,
                    is_2_gon_multiple_component,
                    component_idx1,
                    component_idx2,
                )
                for p in new_smoothed_pairs:
                    t = tuple(p)
                    if t not in smoothed_pairs:
                        smoothed_pairs.append(t)
                something_smoothed = True
                continue


            # 3-gon in the link
            (
                triangle,
                c1,
                i1,
                j1,
                c2,
                i2,
                j2,
                c3,
                i3,
                j3,
                is_true_3_gon,
            ) = identify_3_gon(gauss_code, smoothed_crossings)


            if is_true_3_gon:
                # Triangle smoothing branch
                gauss_code_triangle, smoothed_crossings_triangle, smoothed_pairs_triangle = smooth_3_gon_triangle(
                    gauss_code,
                    triangle,
                    smoothed_crossings,
                    smoothed_pairs,
                    c1,
                    i1,
                    j1,
                    c2,
                    i2,
                    j2,
                    c3,
                    i3,
                    j3,
                )


                # Anti-triangle branch
                gauss_code_anti_triangle, smoothed_crossings_anti_triangle = smooth_3_gon_anti_triangle(
                    gauss_code,
                    triangle,
                    smoothed_crossings,
                    c1,
                    i1,
                    j1,
                    c2,
                    i2,
                    j2,
                    c3,
                    i3,
                    j3,
                )


                # Recurse down both branches
                state_code_triangle = _process_branch(
                    gauss_code_triangle,
                    smoothed_crossings_triangle,
                    smoothed_pairs_triangle,
                    original_gauss_code,
                )
                state_code_anti_triangle = _process_branch(
                    gauss_code_anti_triangle,
                    smoothed_crossings_anti_triangle,
                    smoothed_pairs,
                    original_gauss_code,
                )


                # Choose the branch with minimal genus
                genus_triangle = calculate_unoriented_genus(original_gauss_code, state_code_triangle)
                genus_anti_triangle = calculate_unoriented_genus(original_gauss_code, state_code_anti_triangle)


                if genus_triangle <= genus_anti_triangle:
                    return state_code_triangle
                else:
                    return state_code_anti_triangle
                

        # ------------------------------------------------------------------
        # Case 2: single component
        # ------------------------------------------------------------------
        else:
            component = gauss_code


            # If everything in this component has been smoothed, it forms a state circle
            if all(c in smoothed_crossings for c in component):
                pair = tuple(component)
                if pair not in smoothed_pairs:
                    smoothed_pairs.append(pair)
                break


            # 1-gon
            (
                component_idx,
                start_position,
                end_position,
                pair,
                is_true_1_gon,
                updated_gauss_code,
            ) = identify_1_gon(component, smoothed_crossings)


            if is_true_1_gon:
                smoothed_pairs.append(pair)
                gauss_code, smoothed_crossings = smooth_1_gon(
                    updated_gauss_code,
                    start_position,
                    end_position,
                    smoothed_crossings,
                    component_idx,
                )
                something_smoothed = True
                continue


            # 2-gon
            (
                case,
                a1,
                b1,
                a2,
                b2,
                pair,
                is_true_2_gon,
                is_2_gon_multiple_component,
                component_idx1,
                component_idx2,
                updated_gauss_code,
            ) = identify_2_gon(component, smoothed_crossings)


            if is_true_2_gon:
                gauss_code, smoothed_crossings, new_smoothed_pairs = smooth_2_gon(
                    updated_gauss_code,
                    case,
                    a1,
                    b1,
                    a2,
                    b2,
                    smoothed_crossings,
                    is_2_gon_multiple_component,
                    component_idx1,
                    component_idx2,
                )
                for p in new_smoothed_pairs:
                    t = tuple(p)
                    if t not in smoothed_pairs:
                        smoothed_pairs.append(t)


                something_smoothed = True
                continue


            # 3-gon
            (
                triangle,
                c1,
                i1,
                j1,
                c2,
                i2,
                j2,
                c3,
                i3,
                j3,
                is_true_3_gon,
            ) = identify_3_gon(component, smoothed_crossings)


            if is_true_3_gon:
                # Triangle branch
                gauss_code_triangle, smoothed_crossings_triangle, smoothed_pairs_triangle = smooth_3_gon_triangle(
                    component,
                    triangle,
                    smoothed_crossings,
                    smoothed_pairs,
                    c1,
                    i1,
                    j1,
                    c2,
                    i2,
                    j2,
                    c3,
                    i3,
                    j3,
                )


                # Anti-triangle branch
                gauss_code_anti_triangle, smoothed_crossings_anti_triangle = smooth_3_gon_anti_triangle(
                    component,
                    triangle,
                    smoothed_crossings,
                    c1,
                    i1,
                    j1,
                    c2,
                    i2,
                    j2,
                    c3,
                    i3,
                    j3,
                )


                # Recurse down both branches
                state_code_triangle = _process_branch(
                    gauss_code_triangle,
                    smoothed_crossings_triangle,
                    smoothed_pairs_triangle,
                    original_gauss_code,
                )
                state_code_anti_triangle = _process_branch(
                    gauss_code_anti_triangle,
                    smoothed_crossings_anti_triangle,
                    smoothed_pairs,
                    original_gauss_code,
                )


                # Choose minimal genus
                genus_triangle = calculate_unoriented_genus(original_gauss_code, state_code_triangle)
                genus_anti_triangle = calculate_unoriented_genus(original_gauss_code, state_code_anti_triangle)


                if genus_triangle <= genus_anti_triangle:
                    return state_code_triangle
                else:
                    return state_code_anti_triangle


        # ------------------------------------------------------------------
        # If nothing else can be smoothed, wrap up any fully-smoothed components
        # ------------------------------------------------------------------
        if not something_smoothed:
            if _is_list_of_components(gauss_code):
                for comp in gauss_code:
                    if all(c in smoothed_crossings for c in comp):
                        pair = tuple(comp)
                        if pair not in smoothed_pairs:
                            smoothed_pairs.append(pair)

            break     


    return smoothed_pairs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def process_gauss_code(gauss_code: Any) -> List[Tuple[int, ...]]:
    """
    Run the full smoothing algorithm starting from a Gauss code.


    Args:
        gauss_code:
            - list[int] for a single component,
            - list[list[int]] for multiple components,
            - or a Gauss-notation string.


    Returns:
        state_code: list of tuples, each tuple representing a state circle.
    """

    normalized = _normalize_gauss_code(gauss_code)
    original = copy.deepcopy(normalized)
    state_code = _process_branch(normalized, [], [], original)
    return state_code


def compute_invariants(gauss_code: Any, state_code: Sequence[Sequence[int]]) -> Dict[str, Any]:
    """
    Compute unoriented genus, crosscap, simplicity, and two-sidedness
    from a Gauss code and its state code.
    """

    normalized = _normalize_gauss_code(gauss_code)
    genus = calculate_unoriented_genus(normalized, state_code)
    simple = is_simple(state_code)
    two_sided = is_two_sided(state_code)
    crosscap = calculate_crosscap_number(genus, state_code)


    return {
        "unoriented_genus": genus,
        "crosscap": crosscap,
        "is_simple": simple,
        "is_two_sided": two_sided
    }


def run_pipeline(gauss_code: Any | None = None, dt_code: Any | None = None) -> Dict[str, Any]:
    """
    High-level convenience function.


    Exactly one of 'gauss_code' or 'dt_code' must be provided.

    - If 'dt_code' is provided, it is first converted to a Gauss code via dt_to_gauss.
    - Then the algorithm computes the Kauffman state code and invariants.


    Returns:
        A dictionary with:
            {
                "gauss_code": normalized_gauss_code,
                "state_code": state_code,
                "unoriented_genus": ...,
                "crosscap": ...,
                "is_simple": ...,
                "is_two_sided": ...,
            }
    """

    if (gauss_code is None) == (dt_code is None):
        raise ValueError("Provide exactly one of 'gauss_code' or 'dt_code'.")
    

    if dt_code is not None:
        # Let dt_to_gauss handle list-of-tuples or similar formats
        gauss_code = dt_to_gauss(dt_code)


    if gauss_code is None:
        raise ValueError("No Gauss code available after DT conversion.")
    

    normalized_gauss_code = _normalize_gauss_code(gauss_code)
    state_code = process_gauss_code(normalized_gauss_code)
    invariant = compute_invariants(normalized_gauss_code, state_code)


    result: Dict[str, Any] = {
        "gauss_code": normalized_gauss_code,
        "state_code": state_code,
    }
    result.update(invariant)
    return result
