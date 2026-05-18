import pytest

from state_surfaces.dt_to_gauss import dt_to_gauss


def test_dt_to_gauss_trefoil():
    assert dt_to_gauss([[4, 6, 2]]) == [[1, 2, 3, 1, 2, 3]]


def test_dt_to_gauss_accepts_flat_single_component():
    assert dt_to_gauss([4, 6, 2]) == [[1, 2, 3, 1, 2, 3]]


def test_dt_to_gauss_accepts_string_input():
    assert dt_to_gauss("[[4, 6, 2]]") == [[1, 2, 3, 1, 2, 3]]


def test_dt_to_gauss_uses_absolute_values():
    assert dt_to_gauss([[-4, -6, -2]]) == [[1, 2, 3, 1, 2, 3]]


def test_dt_to_gauss_rejects_out_of_bounds_entry():
    with pytest.raises(ValueError):
        dt_to_gauss([[4, 6, 20]])
        