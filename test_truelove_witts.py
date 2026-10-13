"""Smoke tests for the clinical assessment public entry points."""
from truelove_witts import assess_truelove_witts, calculate_metrics


def test_truelove_witts_single():
    values = dict(stools_per_day=6, blood="visible", pulse_bpm=100,
                  temperature_c=37.0, hemoglobin_g_dl=12.0)
    assert assess_truelove_witts(**values)["classification"] == "Severe"
    assert calculate_metrics(**values)["acute_severe_criteria_met"] is True
