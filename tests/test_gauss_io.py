"""
Regression tests for Gauss-code input normalization utilities.
"""

import pytest

from state_surfaces.gauss_io import clean_gauss_notation


def test_clean_gauss_flat_list():
    assert clean_gauss_notation([1, 2, 3, 1, 2, 3]) == [
        [1, 2, 3, 1, 2, 3]
    ]


def test_clean_gauss_multi_component_list():
    assert clean_gauss_notation([[1, 2], [1, 2]]) == [
        [1, 2],
        [1, 2],
    ]


def test_clean_gauss_uses_absolute_values():
    assert clean_gauss_notation([[1, -2, 3], [-1, 2, -3]]) == [
        [1, 2, 3],
        [1, 2, 3],
    ]


def test_clean_gauss_string_list():
    assert clean_gauss_notation("[[1, 2], [1, 2]]") == [
        [1, 2],
        [1, 2],
    ]


def test_clean_gauss_flat_string_list():
    assert clean_gauss_notation("[1, 2, 3, 1, 2, 3]") == [
        [1, 2, 3, 1, 2, 3]
    ]


def test_clean_gauss_rejects_invalid_string():
    with pytest.raises(ValueError):
        clean_gauss_notation("not a gauss code")
        