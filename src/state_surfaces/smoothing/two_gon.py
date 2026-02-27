"""
smoothing/two_gon.py

Identify and smooth 2-gons (bigons) in Gauss codes.

A "2-gon" is detected when two distinct crossings (a, b) appear in a pattern
that supports a bigon smoothing, with ONLY already-smoothed crossings in the
segments between occurrences (wraparound-aware because Gauss codes are cyclic).

Conventions
-----------
- A Gauss code can be either:
    * single-component: list[int]
    * multi-component:  list[list[int]]

- smoothed_crossings is a list[int] tracking which crossings are already smoothed.

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


def identify_2_gon(gauss_code: GaussCode, smoothed_crossings: List[int],) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[Tuple[int, int]], bool, bool, int, int, Optional[GaussCode],]:
    """
    Identify a 2-gon (bigon) in the Gauss code.

    Returns
    -------
    (
      case, a1, b1, a2, b2, pair,
      is_true_2_gon, is_2_gon_multiple_component,
      component_idx1, component_idx2,
      updated_gauss_code
    )

    Cases
    -----
    Single-component:
      - Case 1: a ... b ... b ... a   (non-wraparound or wraparound via modular indices)
      - Case 2: a ... b ... a ... b   (wraparound-style arrangement)

    Multi-component:
      - Case 3: component1 has (a ... b), component2 has (a ... b)
      - Case 4: component1 has (a ... b), component2 has (b ... a)

    Notes
    -----
    - When a 2-gon is found, the involved component(s) are rotated so the first
      relevant occurrence is at index 0.
    - Index outputs (a1,b1,a2,b2) are offsets in the shifted component(s), not
      absolute indices in the original unshifted components.
    """
    # Unwrap single-list-in-list
    if not has_multiple_components(gauss_code) and isinstance(gauss_code, list) and gauss_code and isinstance(gauss_code[0], list):
        gauss_code = gauss_code[0]  # type: ignore[assignment,index]

    # -----------------------------
    # Multi-component (Cases 3 & 4, plus fallback to per-component Cases 1 & 2)
    # -----------------------------
    if has_multiple_components(gauss_code):
        comps: List[List[int]] = gauss_code  # type: ignore[assignment]
        num_components = len(comps)

        # Try across ALL ordered pairs of distinct components (idx1 != idx2)
        for idx1 in range(num_components):
            for idx2 in range(num_components):
                if idx1 == idx2:
                    continue

                comp1 = comps[idx1]
                comp2 = comps[idx2]
                n1 = len(comp1)
                n2 = len(comp2)
                if n1 == 0 or n2 == 0:
                    continue

                for i in range(n1):
                    a = comp1[i]
                    if a in smoothed_crossings:
                        continue

                    for j in range(i + 1, i + n1):
                        b = comp1[j % n1]
                        if b in smoothed_crossings:
                            continue

                        # segment between a (at i) and b (at j) must be all smoothed
                        start = (i + 1) % n1
                        end = j % n1
                        if start <= end:
                            in_between_1 = comp1[start:end]
                        else:
                            in_between_1 = comp1[start:] + comp1[:end]

                        if any(c not in smoothed_crossings for c in in_between_1):
                            continue

                        # ---- Case 3: component2 contains (a ... b) with only smoothed between
                        for k in range(n2):
                            if comp2[k] != a:
                                continue
                            for m in range(k + 1, k + n2):
                                b2 = comp2[m % n2]
                                if b2 != b or b2 in smoothed_crossings:
                                    continue

                                start2 = (k + 1) % n2
                                end2 = m % n2
                                if start2 <= end2:
                                    in_between_2 = comp2[start2:end2]
                                else:
                                    in_between_2 = comp2[start2:] + comp2[:end2]

                                if any(c not in smoothed_crossings for c in in_between_2):
                                    continue

                                # Found case 3: shift comp1 at i, comp2 at k
                                shifted1 = shift_to_start(comp1, i % n1)
                                shifted2 = shift_to_start(comp2, k % n2)

                                updated = comps[:]
                                updated[idx1] = shifted1
                                updated[idx2] = shifted2

                                # In the shifted comp2, find b index as b2 position
                                index_b = shifted2.index(b)
                                return (
                                    3,
                                    0,
                                    (j - i) % n1,
                                    0,
                                    index_b,
                                    (a, b),
                                    True,
                                    False,
                                    idx1,
                                    idx2,
                                    updated,
                                )

                        # ---- Case 4: component2 contains (b ... a) with only smoothed between
                        for k in range(n2):
                            if comp2[k] != b:
                                continue
                            for m in range(k + 1, k + n2):
                                a2 = comp2[m % n2]
                                if a2 != a or a2 in smoothed_crossings:
                                    continue

                                start2 = (k + 1) % n2
                                end2 = m % n2
                                if start2 <= end2:
                                    in_between_2 = comp2[start2:end2]
                                else:
                                    in_between_2 = comp2[start2:] + comp2[:end2]

                                if any(c not in smoothed_crossings for c in in_between_2):
                                    continue

                                shifted1 = shift_to_start(comp1, i % n1)
                                shifted2 = shift_to_start(comp2, k % n2)

                                updated = comps[:]
                                updated[idx1] = shifted1
                                updated[idx2] = shifted2

                                index_a = shifted2.index(a)
                                return (
                                    4,
                                    0,
                                    (j - i) % n1,
                                    index_a,
                                    0,
                                    (a, b),
                                    True,
                                    False,
                                    idx1,
                                    idx2,
                                    updated,
                                )

        # If no across-component 2-gon, check each component individually for Cases 1 & 2
        for comp_idx, component in enumerate(comps):
            n = len(component)
            if n == 0:
                continue

            for i in range(n):
                a = component[i]
                if a in smoothed_crossings:
                    continue

                for j in range(i + 1, i + n):
                    b = component[j % n]
                    if b in smoothed_crossings:
                        continue

                    start = (i + 1) % n
                    end = j % n
                    if start <= end:
                        in_between_1 = component[start:end]
                    else:
                        in_between_1 = component[start:] + component[:end]

                    if any(c not in smoothed_crossings for c in in_between_1):
                        continue

                    # ---- Case 2: a ... b ... a ... b (wraparound style)
                    for k in range(j + 1, j + n):
                        if component[k % n] != a:
                            continue

                        for m in range(k + 1, n + i):
                            b2 = component[m % n]
                            if b2 != b or b2 in smoothed_crossings:
                                continue

                            start2 = (k + 1) % n
                            end2 = m % n
                            if start2 <= end2:
                                in_between_2 = component[start2:end2]
                            else:
                                in_between_2 = component[start2:] + component[:end2]

                            if any(c not in smoothed_crossings for c in in_between_2):
                                continue

                            shifted = shift_to_start(component, i % n)
                            updated = comps[:]
                            updated[comp_idx] = shifted

                            return (
                                2,
                                0,
                                (j - i) % n,
                                (k - i) % n,
                                (m - i) % n,
                                (a, b),
                                True,
                                True,
                                comp_idx,
                                0,
                                updated,
                            )

                    # ---- Case 1: a ... b ... b ... a
                    for k in range(j + 1, j + n):
                        if component[k % n] != b:
                            continue

                        for m in range(k + 1, n + i):
                            a2 = component[m % n]
                            if a2 != a or a in smoothed_crossings:
                                continue

                            start2 = (k + 1) % n
                            end2 = m % n
                            if start2 <= end2:
                                in_between_2 = component[start2:end2]
                            else:
                                in_between_2 = component[start2:] + component[:end2]

                            if any(c not in smoothed_crossings for c in in_between_2):
                                continue

                            shifted = shift_to_start(component, i % n)
                            updated = comps[:]
                            updated[comp_idx] = shifted

                            return (
                                1,
                                0,
                                (j - i) % n,
                                (m - i) % n,
                                (k - i) % n,
                                (a, b),
                                True,
                                True,
                                comp_idx,
                                0,
                                updated,
                            )

        return None, None, None, None, None, None, False, False, 0, 0, None

    # -----------------------------
    # Single-component (Cases 1 & 2)
    # -----------------------------
    comp: List[int] = gauss_code  # type: ignore[assignment]
    n = len(comp)
    if n == 0:
        return None, None, None, None, None, None, False, False, 0, 0, None

    for i in range(n):
        a = comp[i]
        if a in smoothed_crossings:
            continue

        for j in range(i + 1, i + n):
            b = comp[j % n]
            if b in smoothed_crossings:
                continue

            start = (i + 1) % n
            end = j % n
            if start <= end:
                in_between_1 = comp[start:end]
            else:
                in_between_1 = comp[start:] + comp[:end]

            if any(c not in smoothed_crossings for c in in_between_1):
                continue

            # ---- Case 2: a ... b ... a ... b
            for k in range(j + 1, j + n):
                if comp[k % n] != a:
                    continue

                for m in range(k + 1, k + n):
                    b2 = comp[m % n]
                    if b2 != b or b2 in smoothed_crossings:
                        continue

                    # Avoid false wraparound re-detection with same index positions
                    if (i % n == k % n) and (j % n == m % n):
                        continue

                    start2 = (k + 1) % n
                    end2 = m % n
                    if start2 <= end2:
                        in_between_2 = comp[start2:end2]
                    else:
                        in_between_2 = comp[start2:] + comp[:end2]

                    if any(c not in smoothed_crossings for c in in_between_2):
                        continue

                    shifted = shift_to_start(comp, i % n)
                    return (
                        2,
                        0,
                        (j - i) % n,
                        (k - i) % n,
                        (m - i) % n,
                        (a, b),
                        True,
                        False,
                        0,
                        0,
                        shifted,
                    )

            # ---- Case 1: a ... b ... b ... a
            for k in range(j + 1, j + n):
                if comp[k % n] != b:
                    continue

                for m in range(k + 1, k + n):
                    a2 = comp[m % n]
                    if a2 != a or a in smoothed_crossings:
                        continue

                    # Avoid false wraparound re-detection with same index positions
                    if (i % n == m % n) and (j % n == k % n):
                        continue

                    start2 = (k + 1) % n
                    end2 = m % n
                    if start2 <= end2:
                        in_between_2 = comp[start2:end2]
                    else:
                        in_between_2 = comp[start2:] + comp[:end2]

                    if any(c not in smoothed_crossings for c in in_between_2):
                        continue

                    shifted = shift_to_start(comp, i % n)
                    return (
                        1,
                        0,
                        (j - i) % n,
                        (m - i) % n,
                        (k - i) % n,
                        (a, b),
                        True,
                        False,
                        0,
                        0,
                        shifted,
                    )

    return None, None, None, None, None, None, False, False, 0, 0, None


def smooth_2_gon(gauss_code: GaussCode, case: int, a1: int, b1: int, a2: int, b2: int, smoothed_crossings: List[int], is_2_gon_multiple_component: bool, component_idx1: int, component_idx2: int,) -> Tuple[GaussCode, List[int], List[Tuple[int, ...]]]:
    """
    Smooth a detected 2-gon.

    Returns
    -------
    (new_gauss_code, smoothed_crossings, smoothed_pairs_added)

    Notes
    -----
    This function includes:
    - which segments are reversed
    - which new components are produced per case
    - the exact structure of `smoothed_pairs` (state circle tuple)
    """
    # Cases 1 & 2: smoothing within one component
    if case in (1, 2):
        if is_2_gon_multiple_component:
            affected = gauss_code[component_idx1]  # type: ignore[index]
            a = affected[a1]
            b = affected[b1]
        else:
            affected = gauss_code  # type: ignore[assignment]
            a = affected[a1]       # type: ignore[index]
            b = affected[b1]       # type: ignore[index]

        # mark crossings smoothed
        if a not in smoothed_crossings:
            smoothed_crossings.append(a)
        if b not in smoothed_crossings:
            smoothed_crossings.append(b)

        if case == 1:
            # Pattern: a (s1) b (w0) b (s2) a (w1)
            s1 = affected[a1 + 1 : b1]
            s2 = affected[b2 + 1 : a2]
            w0 = affected[b1 + 1 : b2]
            w1 = affected[a2 + 1 :]

            smoothed_pairs = [(a, *s1, b, *s2) if (s1 or s2) else (a, b)]

            component_1 = [a] + w1
            component_2 = [b] + w0

            if is_2_gon_multiple_component:
                new_gauss_code = gauss_code[:component_idx1] + gauss_code[component_idx1 + 1 :]  # type: ignore[operator]
                new_gauss_code.extend([component_1, component_2])  # type: ignore[union-attr]
            else:
                new_gauss_code = [component_1, component_2]

            return new_gauss_code, smoothed_crossings, smoothed_pairs

        # case == 2
        # Pattern: a (s1) b (w0) a (s2 reversed) b (w1)
        s1 = affected[a1 + 1 : b1]
        s2 = affected[a2 + 1 : b2][::-1]
        w0 = affected[b1 + 1 : a2]
        w1 = affected[b2 + 1 :]

        smoothed_pairs = [(a, *s1, b, *s2) if (s1 or s2) else (a, b)]

        new_component = [a] + w0[::-1] + [b] + w1

        if is_2_gon_multiple_component:
            new_gauss_code = gauss_code[:component_idx1] + gauss_code[component_idx1 + 1 :]  # type: ignore[operator]
            new_gauss_code.extend([new_component])  # type: ignore[union-attr]
        else:
            new_gauss_code = [new_component]

        return new_gauss_code, smoothed_crossings, smoothed_pairs

    # Cases 3 & 4: smoothing across two different components
    if case in (3, 4):
        comps: List[List[int]] = gauss_code  # type: ignore[assignment]
        comp1 = comps[component_idx1]
        comp2 = comps[component_idx2]

        a = comp1[a1]
        b = comp1[b1]

        if a not in smoothed_crossings:
            smoothed_crossings.append(a)
        if b not in smoothed_crossings:
            smoothed_crossings.append(b)

        if case == 3:
            # comp1: a (s1) b (w0)
            s1 = comp1[a1 + 1 : b1]
            w0 = comp1[b1 + 1 :]

            # comp2: a ( ... ) b, but we were shifted to start at a, so:
            s2 = comp2[a2 + 1 : b2][::-1]
            w1 = comp2[b2 + 1 :]

            smoothed_pairs = [(a, *s1, b, *s2) if (s1 or s2) else (a, b)]

            new_component = [a] + w1[::-1] + [b] + w0

            new_gauss_code = [
                comp for idx, comp in enumerate(comps)
                if idx not in (component_idx1, component_idx2)
            ]
            new_gauss_code.append(new_component)

            return new_gauss_code, smoothed_crossings, smoothed_pairs

        # case == 4
        s1 = comp1[a1 + 1 : b1]
        w0 = comp1[b1 + 1 :]

        s2 = comp2[b2 + 1 : a2]
        w1 = comp2[a2 + 1 :]

        smoothed_pairs = [(a, *s1, b, *s2) if (s1 or s2) else (a, b)]

        new_component = [a] + w1 + [b] + w0

        new_gauss_code = [
            comp for idx, comp in enumerate(comps)
            if idx not in (component_idx1, component_idx2)
        ]
        new_gauss_code.append(new_component)

        return new_gauss_code, smoothed_crossings, smoothed_pairs

    # If case is unknown, do nothing
    return gauss_code, smoothed_crossings, []
