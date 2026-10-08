"""Independent numerical and invalid-input controls for representation sensitivity."""
import pytest
from research.network_reading.study import profile


def test_threshold_projection_retains_isolates_and_exact_pair_denominator():
    rows = [frozenset({0, 1}), frozenset({0, 1, 2}), frozenset({2}), frozenset()]
    cells = profile(rows, 4, [2, 4], [1, 2, 3])
    first = cells[3]
    assert first['edges'] == 3 and first['possible_pairs'] == 6
    assert first['density'] == .5
    assert first['mean_local_clustering'] == .75
    assert first['isolated_terms'] == 1 and first['components'] == 2
    strict = cells[4]
    assert strict['edges'] == 1 and strict['density'] == pytest.approx(1/6)
    assert strict['mean_local_clustering'] == 0 and strict['isolated_terms'] == 2
    assert cells[5]['edges'] == 0 and cells[5]['components'] == 4
    assert cells[0]['density'] == 1 and cells[0]['documents_with_selected_terms'] == 2


@pytest.mark.parametrize('sizes,thresholds', [([1],[1]),([5],[1]),([2,2],[1]),([2],[0]),([2],[True]),([],[1]),([2],[])])
def test_invalid_diagnostic_protocol_rejected(sizes, thresholds):
    with pytest.raises(ValueError):
        profile([frozenset({0}), frozenset({1})], 4, sizes, thresholds)


@pytest.mark.parametrize('rows', [[frozenset(),frozenset()], [frozenset({4}),frozenset()], [frozenset({True}),frozenset()]])
def test_empty_or_invalid_incidence_rejected(rows):
    with pytest.raises(ValueError):
        profile(rows, 4, [4], [1])
