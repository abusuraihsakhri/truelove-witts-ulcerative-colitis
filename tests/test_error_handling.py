"""
Automated Pytest for error handling and edge cases in truelove-witts-ulcerative-colitis.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import math
from truelove_witts import calculate_metrics, process_batch
from cli import main as cli_main


class TestCalculateMetricsEdgeCases:
    """Test edge cases for calculate_metrics function."""

    def test_nan_values_are_ignored(self):
        """NaN values should be skipped in calculation."""
        res = calculate_metrics(v1=10.0, v2=float('nan'), v3=5.0)
        assert "score" in res
        assert not math.isnan(res["score"])

    def test_inf_values_are_ignored(self):
        """Infinity values should be skipped in calculation."""
        res = calculate_metrics(v1=10.0, v2=float('inf'), v3=5.0)
        assert "score" in res
        assert not math.isinf(res["score"])

    def test_negative_inf_values_are_ignored(self):
        """Negative infinity values should be skipped in calculation."""
        res = calculate_metrics(v1=10.0, v2=float('-inf'), v3=5.0)
        assert "score" in res
        assert not math.isinf(res["score"])

    def test_all_nan_values_uses_default(self):
        """When all values are NaN, should use default primary_val of 1.0."""
        res = calculate_metrics(v1=float('nan'), v2=float('nan'))
        assert res["score"] == 1.0

    def test_empty_params_uses_default(self):
        """When no params provided, should use default primary_val of 1.0."""
        res = calculate_metrics()
        assert res["score"] == 1.0

    def test_string_values_are_preserved(self):
        """Non-numeric string values should be preserved as strings."""
        res = calculate_metrics(v1=10.0, label="test")
        assert res["inputs_evaluated"] == 2

    def test_classification_low(self):
        """Score < 10 should be classified as Low/Standard."""
        res = calculate_metrics(v1=5.0)
        assert res["classification"] == "Low / Standard"

    def test_classification_moderate(self):
        """10 <= Score < 25 should be classified as Moderate/Intermediate."""
        res = calculate_metrics(v1=15.0)
        assert res["classification"] == "Moderate / Intermediate"

    def test_classification_high(self):
        """Score >= 25 should be classified as High/Severe."""
        res = calculate_metrics(v1=30.0)
        assert res["classification"] == "High / Severe"


class TestProcessBatchErrorHandling:
    """Test error handling for process_batch function."""

    def test_file_not_found_raises_error(self, tmp_path):
        """Non-existent input file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            process_batch(str(tmp_path / "nonexistent.csv"), str(tmp_path / "out.csv"))

    def test_empty_csv_raises_error(self, tmp_path):
        """Empty CSV file should raise ValueError."""
        csv_in = tmp_path / "empty.csv"
        csv_in.write_text("", encoding="utf-8")
        with pytest.raises(ValueError):
            process_batch(str(csv_in), str(tmp_path / "out.csv"))

    def test_csv_no_headers_raises_error(self, tmp_path):
        """CSV with no headers should raise ValueError."""
        csv_in = tmp_path / "noheaders.csv"
        csv_in.write_text("\n", encoding="utf-8")
        with pytest.raises(ValueError):
            process_batch(str(csv_in), str(tmp_path / "out.csv"))

    def test_valid_batch_processing(self, tmp_path):
        """Valid CSV should process correctly."""
        csv_in = tmp_path / "valid.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text("Patient_ID,v1,v2\nPT-001,10.0,5.0\n", encoding="utf-8")
        process_batch(str(csv_in), str(csv_out))
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "PT-001" in content


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_batch_missing_file_returns_error_code(self):
        """CLI batch with non-existent file should return error code 1."""
        result = cli_main(["batch", "-i", "nonexistent_file_12345.csv"])
        assert result == 1

    def test_batch_valid_file_returns_success(self, tmp_path):
        """CLI batch with valid file should return success code 0."""
        csv_in = tmp_path / "valid.csv"
        csv_in.write_text("task_id,target_identifier,primary_metric,secondary_metric\nT1,KEY-01,10.0,5.0\n", encoding="utf-8")
        result = cli_main(["batch", "-i", str(csv_in)])
        assert result == 0
