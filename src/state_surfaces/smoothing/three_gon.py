"""
smoothing/three_gon.py

Detection logic for 3-gons (triangles) in Gauss codes.

This module only identifies 3-gons. The two possible smoothing branches are
implemented separately in:
    - three_gon_triangle.py
    - three_gon_anti_triangle.py
"""

from __future__ import annotations


def identify_3_gon(gauss_code, smoothed_crossings):
    # Ensure gauss_code is in multi-component format
    if all(isinstance(x, int) for x in gauss_code):
        gauss_code = [gauss_code]  # Wrap single component in a list

    found_3_gons = set()  # To prevent duplicate detections

    # === Step 1: Collect all valid (a, b) pairs across components ===
    # A valid pair (a, b) has only smoothed crossings in between.
    pairs = []  # Each entry is: ((a, b), component_index, index_a, index_b)
    for comp_idx, component in enumerate(gauss_code):
        n = len(component)
        for i in range(n):
            a = component[i]
            if a in smoothed_crossings:
                continue
            for j in range(1, n):
                b = component[(i + j) % n]
                if b == a or b in smoothed_crossings:
                    continue

                # Get in-between segment from a to b (wraparound-aware)
                if i < (i + j) % n:
                    in_between = component[i + 1:(i + j) % n]
                else:
                    in_between = component[i + 1:] + component[:(i + j) % n]

                # All intermediate crossings must be smoothed
                if any(c not in smoothed_crossings for c in in_between):
                    continue

                # Valid (a, b) pair found
                pairs.append(((a, b), comp_idx, i, (i + j) % n))

    # === Step 2: Search for a 3-gon ===
    # Look for three distinct pairs forming (a, b), (b, c), and (a, c)
    for (pair1, c1, i1, j1) in pairs:
        a, b = pair1
        for (pair2, c2, i2, j2) in pairs:
            if (c2, i2) == (c1, i1):  # Skip same pair
                continue
            if b not in pair2:  # We want (b, c)
                continue

            # Extract c from the second pair
            c = pair2[1] if pair2[0] == b else pair2[0]
            if c == a or c in smoothed_crossings:
                continue

            for (pair3, c3, i3, j3) in pairs:
                if (c3, i3) in [(c1, i1), (c2, i2)]:
                    continue

                # We want (a, c) as the third side
                if a in pair3 and c in pair3:

                    # Verify all crossings in between are smoothed
                    def get_in_between(component, i, j):
                        n = len(component)
                        return component[i + 1:j] if i < j else component[i + 1:] + component[:j]

                    in_between_1 = get_in_between(gauss_code[c1], i1, j1)
                    in_between_2 = get_in_between(gauss_code[c2], i2, j2)
                    in_between_3 = get_in_between(gauss_code[c3], i3, j3)

                    if any(
                        crossing not in smoothed_crossings
                        for crossing in in_between_1 + in_between_2 + in_between_3
                    ):
                        continue

                    # Normalize the triangle so we don't find duplicates
                    standardized = tuple(sorted([a, b, c]))
                    if standardized not in found_3_gons:
                        found_3_gons.add(standardized)

                        # Return all index info for smoothing
                        return (a, b, c), c1, i1, j1, c2, i2, j2, c3, i3, j3, True

    return None, None, None, None, None, None, None, None, None, None, False
