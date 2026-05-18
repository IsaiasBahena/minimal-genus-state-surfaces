"""
High-level pipeline for computing state codes and surface invariants.

The pipeline starts from either a Gauss code or a Dowker-Thistlethwaite (DT)
code, applies the recursive smoothing algorithm, and computes the resulting
unoriented genus, crosscap number, simplicity, and two-sidedness.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Sequence, Tuple

from .dt_to_gauss import dt_to_gauss
from .gauss_io import clean_gauss_notation
from .genus import calculate_unoriented_genus
from .nonorientable import calculate_crosscap_number, is_simple, is_two_sided
from .smoothing.one_gon import identify_1_gon, smooth_1_gon
from .smoothing.three_gon import identify_3_gon
from .smoothing.three_gon_anti_triangle import smooth_3_gon_anti_triangle
from .smoothing.three_gon_triangle import smooth_3_gon_triangle
from .smoothing.two_gon import identify_2_gon, smooth_2_gon


def _has_multiple_components(gauss_code: Any) -> bool:
    """Return True if the Gauss code has two or more components."""
    return (
        isinstance(gauss_code, list)
        and len(gauss_code) > 1
        and all(isinstance(comp, list) for comp in gauss_code)
    )


def _is_list_of_components(gauss_code: Any) -> bool:
    """Return True if the Gauss code is represented as list[list[int]]."""
    return (
        isinstance(gauss_code, list)
        and all(isinstance(comp, list) for comp in gauss_code)
    )


def _normalize_gauss_code(gauss_code: Any) -> List[List[int]]:
    """
    Normalize input into list[list[int]] form with positive crossing labels.

    Accepted formats:
      - list[int] for a single component,
      - list[list[int]] for multiple components,
      - supported Gauss notation strings.
    """
    if isinstance(gauss_code, str):
        return clean_gauss_notation(gauss_code)

    if isinstance(gauss_code, list):
        if gauss_code and all(isinstance(comp, list) for comp in gauss_code):
            return [list(map(abs, comp)) for comp in gauss_code]

        if gauss_code and all(isinstance(x, int) for x in gauss_code):
            return [list(map(abs, gauss_code))]

    return clean_gauss_notation(gauss_code)


def _process_branch(gauss_code: Any, smoothed_crossings: List[int], smoothed_pairs: List[Tuple[int, ...]], original_gauss_code: Any,) -> List[Tuple[int, ...]]:
    """
    Recursively smooth one branch of the state-surface algorithm.

    A branch is determined by the choices made when a 3-gon is found: triangle
    smoothing and anti-triangle smoothing are explored separately, and the
    lower-genus resulting state code is retained.
    """
    smoothed_crossings = copy.deepcopy(smoothed_crossings)
    smoothed_pairs = copy.deepcopy(smoothed_pairs)

    # Unwrap a single component stored as [[...]] into [...].
    if (
        isinstance(gauss_code, list)
        and len(gauss_code) == 1
        and not _has_multiple_components(gauss_code)
    ):
        gauss_code = gauss_code[0]

    while True:
        something_smoothed = False

        # Multiple-component branch.
        if _has_multiple_components(gauss_code):
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
                gauss_code_triangle, smoothed_crossings_triangle, smoothed_pairs_triangle = (
                    smooth_3_gon_triangle(
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
                )

                gauss_code_anti_triangle, smoothed_crossings_anti_triangle = (
                    smooth_3_gon_anti_triangle(
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
                )

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

                genus_triangle = calculate_unoriented_genus(
                    original_gauss_code,
                    state_code_triangle,
                )
                genus_anti_triangle = calculate_unoriented_genus(
                    original_gauss_code,
                    state_code_anti_triangle,
                )

                if genus_triangle <= genus_anti_triangle:
                    return state_code_triangle

                return state_code_anti_triangle

        # Single-component branch.
        else:
            component = gauss_code

            if all(c in smoothed_crossings for c in component):
                pair = tuple(component)
                if pair not in smoothed_pairs:
                    smoothed_pairs.append(pair)
                break

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
                gauss_code_triangle, smoothed_crossings_triangle, smoothed_pairs_triangle = (
                    smooth_3_gon_triangle(
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
                )

                gauss_code_anti_triangle, smoothed_crossings_anti_triangle = (
                    smooth_3_gon_anti_triangle(
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
                )

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

                genus_triangle = calculate_unoriented_genus(
                    original_gauss_code,
                    state_code_triangle,
                )
                genus_anti_triangle = calculate_unoriented_genus(
                    original_gauss_code,
                    state_code_anti_triangle,
                )

                if genus_triangle <= genus_anti_triangle:
                    return state_code_triangle

                return state_code_anti_triangle

        # If no smoothing move applies, add any fully smoothed leftover
        # components as state circles.
        if not something_smoothed:
            if _is_list_of_components(gauss_code):
                for comp in gauss_code:
                    if all(c in smoothed_crossings for c in comp):
                        pair = tuple(comp)
                        smoothed_pairs.append(pair)

            break

    return smoothed_pairs


def process_gauss_code(gauss_code: Any) -> List[Tuple[int, ...]]:
    """
    Run the full smoothing algorithm starting from a Gauss code.

    Parameters
    ----------
    gauss_code:
        Gauss code input accepted by `_normalize_gauss_code`.

    Returns
    -------
    list[tuple[int, ...]]
        State code, represented as a list of state circles.
    """
    normalized = _normalize_gauss_code(gauss_code)
    original = copy.deepcopy(normalized)

    return _process_branch(normalized, [], [], original)


def compute_invariants(gauss_code: Any, state_code: Sequence[Sequence[int]],) -> Dict[str, Any]:
    """
    Compute unoriented genus, crosscap number, simplicity, and two-sidedness.
    """
    normalized = _normalize_gauss_code(gauss_code)

    genus = calculate_unoriented_genus(normalized, state_code)
    simple = is_simple(state_code)
    two_sided = is_two_sided(state_code)
    crosscap = calculate_crosscap_number(genus, state_code)

    return {
        "unoriented_genus": genus,
        "crosscap": crosscap,
        "simple": simple,
        "two_sided": two_sided,
    }


def run_pipeline(gauss_code: Any | None = None, dt_code: Any | None = None,) -> Dict[str, Any]:
    """
    Run the full state-surface pipeline.

    Exactly one of `gauss_code` or `dt_code` must be provided. If a DT code is
    provided, it is first converted to a Gauss code before smoothing.

    Returns
    -------
    dict
        Dictionary containing the normalized Gauss code, state code, and
        computed invariants.
    """
    if (gauss_code is None) == (dt_code is None):
        raise ValueError("Provide exactly one of 'gauss_code' or 'dt_code'.")

    if dt_code is not None:
        gauss_code = dt_to_gauss(dt_code)

    if gauss_code is None:
        raise ValueError("No Gauss code available after DT conversion.")

    normalized_gauss_code = _normalize_gauss_code(gauss_code)
    state_code = process_gauss_code(normalized_gauss_code)
    invariants = compute_invariants(normalized_gauss_code, state_code)

    result: Dict[str, Any] = {
        "gauss_code": normalized_gauss_code,
        "state_code": state_code,
    }
    result.update(invariants)

    return result
