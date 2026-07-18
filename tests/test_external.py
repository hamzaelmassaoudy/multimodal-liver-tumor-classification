import pytest

from liver_tumor_pipeline.external import compare_sex_scenarios


def test_external_sex_scenario_comparison():
    summary = compare_sex_scenarios([0, 0, 0, 2], [0, 1, 1, 2])
    assert summary["primary_hcc_sensitivity"] == pytest.approx(0.75)
    assert summary["sex_zero_hcc_sensitivity"] == pytest.approx(0.25)
    assert summary["changed_predictions"] == 2
