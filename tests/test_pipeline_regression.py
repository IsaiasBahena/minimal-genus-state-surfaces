# tests/test_pipeline_regression.py

from state_surfaces import run_pipeline


def test_trefoil_gauss_code():
    result = run_pipeline(gauss_code=[1, 2, 3, 1, 2, 3])

    assert result["state_code"] == [(1, 2), (3, 2), (3, 1)]
    assert result["unoriented_genus"] == 1
    assert result["crosscap"] == 1
    assert result["simple"] is True
    assert result["two_sided"] is False


def test_special_two_component_link_preserves_duplicate_state_circles():
    result = run_pipeline(gauss_code=[[1, 2], [1, 2]])

    assert result["state_code"] == [(1, 2), (1, 2)]
    assert result["unoriented_genus"] == 1
    assert result["crosscap"] == 2
    assert result["simple"] is True
    assert result["two_sided"] is True


def test_8_18_regression():
    result = run_pipeline(
        gauss_code=[[1, 2, 3, 4, 5, 1, 6, 3, 7, 5, 8, 6, 2, 7, 4, 8]]
    )

    assert result["state_code"] == [
        (1, 2, 6),
        (5, 1, 8),
        (7, 3, 2),
        (4, 8, 6, 3),
        (4, 5, 7),
    ]
    assert result["unoriented_genus"] == 4
    assert result["crosscap"] == 4
    assert result["simple"] is True
    assert result["two_sided"] is False
    