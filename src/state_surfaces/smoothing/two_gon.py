"""
Identify and smooth 2-gons in Gauss codes.

A 2-gon is detected when two distinct crossings form a valid bigon pattern
whose intervening segments contain only already-smoothed crossings. Since
Gauss codes are cyclic, all searches are wraparound-aware.
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


def identify_2_gon(gauss_code: GaussCode, smoothed_crossings: List[int],) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[Tuple[int, int]], bool, bool, int, int, Optional[GaussCode],]:
    """
    Identify a 2-gon in a Gauss code.

    Returns
    -------
    tuple
        (
            case, a1, b1, a2, b2, pair,
            found, is_same_component_case,
            component_idx1, component_idx2,
            updated_gauss_code,
        )

    Notes
    -----
    Cases 1 and 2 occur within one component. Cases 3 and 4 occur across two
    components. When a 2-gon is found, the involved component or components
    are rotated so that the relevant starting crossing is at index 0.
    """
    if (
        not has_multiple_components(gauss_code)
        and isinstance(gauss_code, list)
        and gauss_code
        and isinstance(gauss_code[0], list)
    ):
        gauss_code = gauss_code[0]  # type: ignore[assignment, index]

    # Multi-component cases.
    if has_multiple_components(gauss_code):
        comps: List[List[int]] = gauss_code  # type: ignore[assignment]
        num_components = len(comps)

        # First try 2-gons spanning two distinct components.
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

                        start = (i + 1) % n1
                        end = j % n1

                        if start <= end:
                            in_between_1 = comp1[start:end]
                        else:
                            in_between_1 = comp1[start:] + comp1[:end]

                        if any(c not in smoothed_crossings for c in in_between_1):
                            continue

                        # Case 3: component 2 contains a ... b.
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

                                if any(
                                    c not in smoothed_crossings
                                    for c in in_between_2
                                ):
                                    continue

                                shifted1 = shift_to_start(comp1, i % n1)
                                shifted2 = shift_to_start(comp2, k % n2)

                                updated = comps[:]
                                updated[idx1] = shifted1
                                updated[idx2] = shifted2

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

                        # Case 4: component 2 contains b ... a.
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

                                if any(
                                    c not in smoothed_crossings
                                    for c in in_between_2
                                ):
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

        # If no cross-component 2-gon exists, search each component separately.
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

                    # Case 2: a ... b ... a ... b.
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

                            if any(
                                c not in smoothed_crossings
                                for c in in_between_2
                            ):
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

                    # Case 1: a ... b ... b ... a.
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

                            if any(
                                c not in smoothed_crossings
                                for c in in_between_2
                            ):
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

    # Single-component cases.
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

            # Case 2: a ... b ... a ... b.
            for k in range(j + 1, j + n):
                if comp[k % n] != a:
                    continue

                for m in range(k + 1, k + n):
                    b2 = comp[m % n]
                    if b2 != b or b2 in smoothed_crossings:
                        continue

                    # Avoid false wraparound re-detection at the same indices.
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

            # Case 1: a ... b ... b ... a.
            for k in range(j + 1, j + n):
                if comp[k % n] != b:
                    continue

                for m in range(k + 1, k + n):
                    a2 = comp[m % n]
                    if a2 != a or a in smoothed_crossings:
                        continue

                    # Avoid false wraparound re-detection at the same indices.
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
    tuple
        (new_gauss_code, updated_smoothed_crossings, new_state_circles)
    """
    # Cases 1 and 2: smoothing within one component.
    if case in (1, 2):
        if is_2_gon_multiple_component:
            affected = gauss_code[component_idx1]  # type: ignore[index]
            a = affected[a1]
            b = affected[b1]
        else:
            affected = gauss_code  # type: ignore[assignment]
            a = affected[a1]  # type: ignore[index]
            b = affected[b1]  # type: ignore[index]

        if a not in smoothed_crossings:
            smoothed_crossings.append(a)
        if b not in smoothed_crossings:
            smoothed_crossings.append(b)

        if case == 1:
            # Pattern: a (s1) b (w0) b (s2) a (w1).
            s1 = affected[a1 + 1 : b1]
            s2 = affected[b2 + 1 : a2]
            w0 = affected[b1 + 1 : b2]
            w1 = affected[a2 + 1 :]

            smoothed_pairs = [(a, *s1, b, *s2) if (s1 or s2) else (a, b)]

            component_1 = [a] + w1
            component_2 = [b] + w0

            if is_2_gon_multiple_component:
                new_gauss_code = (
                    gauss_code[:component_idx1]
                    + gauss_code[component_idx1 + 1 :]
                )  # type: ignore[operator]
                new_gauss_code.extend([component_1, component_2])  # type: ignore[union-attr]
            else:
                new_gauss_code = [component_1, component_2]

            return new_gauss_code, smoothed_crossings, smoothed_pairs

        # Case 2 pattern: a (s1) b (w0) a (s2 reversed) b (w1).
        s1 = affected[a1 + 1 : b1]
        s2 = affected[a2 + 1 : b2][::-1]
        w0 = affected[b1 + 1 : a2]
        w1 = affected[b2 + 1 :]

        smoothed_pairs = [(a, *s1, b, *s2) if (s1 or s2) else (a, b)]
        new_component = [a] + w0[::-1] + [b] + w1

        if is_2_gon_multiple_component:
            new_gauss_code = (
                gauss_code[:component_idx1]
                + gauss_code[component_idx1 + 1 :]
            )  # type: ignore[operator]
            new_gauss_code.extend([new_component])  # type: ignore[union-attr]
        else:
            new_gauss_code = [new_component]

        return new_gauss_code, smoothed_crossings, smoothed_pairs

    # Cases 3 and 4: smoothing across two different components.
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
            s1 = comp1[a1 + 1 : b1]
            w0 = comp1[b1 + 1 :]

            s2 = comp2[a2 + 1 : b2][::-1]
            w1 = comp2[b2 + 1 :]

            smoothed_pairs = [(a, *s1, b, *s2) if (s1 or s2) else (a, b)]
            new_component = [a] + w1[::-1] + [b] + w0

            new_gauss_code = [
                comp
                for idx, comp in enumerate(comps)
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
            comp
            for idx, comp in enumerate(comps)
            if idx not in (component_idx1, component_idx2)
        ]
        new_gauss_code.append(new_component)

        return new_gauss_code, smoothed_crossings, smoothed_pairs

    # Unknown case: leave the code unchanged.
    return gauss_code, smoothed_crossings, []
