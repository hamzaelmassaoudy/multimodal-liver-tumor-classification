import pytest

from liver_tumor_pipeline.external import compare_sex_scenarios


def test_external_sex_scenario_comparison():
    summary = compare_sex_scenarios([0, 1, 1, 2], [0, 0, 0, 2])
    assert summary["historical_hcc_sensitivity"] == pytest.approx(0.25)
    assert summary["median_sex_hcc_sensitivity"] == pytest.approx(0.75)
    assert summary["changed_predictions"] == 2
