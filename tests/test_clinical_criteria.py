import csv
import pytest
from truelove_witts import assess_truelove_witts, calculate_metrics, process_batch, main


BASE = dict(stools_per_day=3, blood="small", pulse_bpm=75,
            temperature_c=37.0, hemoglobin_g_dl=13.0,
            esr_mm_h=10, crp_mg_l=2)


def assess(**changes):
    values = dict(BASE)
    values.update(changes)
    return assess_truelove_witts(**values)


def test_mild_and_moderate():
    assert assess()["classification"] == "Mild"
    assert assess(stools_per_day=5, blood="visible")["classification"] == "Moderate"
    assert assess(stools_per_day=3, blood="visible")["classification"] == "Moderate"


@pytest.mark.parametrize("change,marker", [
    ({"pulse_bpm": 91}, "pulse_over_90"),
    ({"temperature_c": 37.9}, "temperature_over_37_8"),
    ({"hemoglobin_g_dl": 10.4}, "hemoglobin_below_10_5"),
    ({"esr_mm_h": 31}, "esr_over_30"),
    ({"crp_mg_l": 31}, "crp_over_30"),
])
def test_severe_with_each_marker(change, marker):
    result = assess(stools_per_day=6, blood="visible", **change)
    assert result["classification"] == "Severe"
    assert marker in result["positive_markers"]


def test_cutoffs_require_strict_systemic_positivity():
    result = assess(stools_per_day=6, blood="visible", pulse_bpm=90,
                    temperature_c=37.8, hemoglobin_g_dl=10.5,
                    esr_mm_h=30, crp_mg_l=30)
    assert result["classification"] == "Moderate"


def test_severe_requires_bloody_frequency_and_toxicity():
    assert assess(stools_per_day=5, blood="visible", pulse_bpm=130)["classification"] == "Moderate"
    assert assess(stools_per_day=7, blood="none", pulse_bpm=130)["classification"] == "Moderate"


def test_missing_markers_are_not_silently_normal():
    result = assess(stools_per_day=7, blood="visible", esr_mm_h=None, crp_mg_l=None)
    assert result["classification"] == "Indeterminate"
    assert set(result["missing_markers"]) == {"esr_over_30", "crp_over_30"}
    assert assess(stools_per_day=7, blood="visible", pulse_bpm=95, esr_mm_h=None,
                  crp_mg_l=None)["classification"] == "Severe"


@pytest.mark.parametrize("change", [
    {"stools_per_day": -1},
    {"stools_per_day": 2.5},
    {"stools_per_day": "NaN"},
    {"pulse_bpm": float("inf")},
    {"hemoglobin_g_dl": -1},
    {"crp_mg_l": -3},
    {"blood": "unknown"},
])
def test_invalid_values_rejected(change):
    with pytest.raises(ValueError):
        assess(**change)


def test_legacy_function_name_uses_real_criteria():
    assert calculate_metrics(**BASE)["classification"] == "Mild"


def test_cli_single(capsys):
    main(["single", "--stools-per-day", "6", "--blood", "visible",
          "--pulse-bpm", "91", "--temperature-c", "37",
          "--hemoglobin-g-dl", "12"])
    assert '"classification": "Severe"' in capsys.readouterr().out


def test_batch_and_formula_protection(tmp_path):
    src = tmp_path / "input.csv"
    dst = tmp_path / "output.csv"
    src.write_text("id,stools_per_day,blood,pulse_bpm,temperature_c,hemoglobin_g_dl,esr_mm_h,crp_mg_l\n"
                   "=CMD,6,visible,91,37,12,,\nX-002,3,small,70,37,13,8,1\n",
                   encoding="utf-8")
    process_batch(src, dst)
    with dst.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [r["classification"] for r in rows] == ["Severe", "Mild"]
    assert rows[0]["id"] == "'=CMD"


def test_batch_rejects_invalid_rows_without_output(tmp_path):
    src = tmp_path / "input.csv"
    dst = tmp_path / "output.csv"
    src.write_text("stools_per_day,blood,pulse_bpm,temperature_c,hemoglobin_g_dl\n"
                   "six,visible,92,38,12\n")
    with pytest.raises(ValueError, match="row 2"):
        process_batch(src, dst)
    assert not dst.exists()


def test_batch_rejects_overwrite(tmp_path):
    src = tmp_path / "input.csv"
    src.write_text("stools_per_day,blood,pulse_bpm,temperature_c,hemoglobin_g_dl\n")
    with pytest.raises(ValueError, match="differ"):
        process_batch(src, src)
