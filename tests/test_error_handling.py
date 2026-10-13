"""Regression checks for input handling, CSV booleans, and audit integrity."""
import csv
import pytest
from agents.base import AuditTrail, PHIGuard, SecurityException
from cli import main as cli_main, parse_boolean


def test_batch_missing_file_returns_error_code(capsys):
    assert cli_main(["batch", "-i", "nonexistent_file_12345.csv"]) == 1


def test_boolean_csv_conversion():
    assert parse_boolean("false") is False
    assert parse_boolean("0") is False
    assert parse_boolean("True") is True
    with pytest.raises(ValueError):
        parse_boolean("maybe")


def test_false_flag_does_not_trigger_emergency(tmp_path):
    src = tmp_path / "in.csv"
    dst = tmp_path / "out.csv"
    src.write_text("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n"
                   "T1,KEY-01,10,1,NOMINAL,False\n", encoding="utf-8")
    assert cli_main(["batch", "-i", str(src), "-o", str(dst)]) == 0
    with dst.open(newline="", encoding="utf-8") as stream:
        row = next(csv.DictReader(stream))
    assert row["overall_urgency"] == "ROUTINE"


def test_audit_detects_modified_signatures_and_fields():
    trail = AuditTrail(secret_key="testing-secret")
    trail.log("tester", "test", "case", {"status": "ok"})
    trail.log("tester", "test", "case", {"status": "ok2"})
    assert trail.verify_integrity() is True
    trail.logs[0]["actor"] = "intruder"
    assert trail.verify_integrity() is False
    trail.logs[0]["actor"] = "tester"
    trail.logs[1]["current_hash"] = "0" * 64
    assert trail.verify_integrity() is False


def test_audit_getter_returns_defensive_copy():
    trail = AuditTrail(secret_key="testing-secret")
    trail.log("tester", "test", "case", {})
    trail.get_trail()[0]["current_hash"] = "f" * 64
    assert trail.verify_integrity() is True


def test_phi_guard_rejects_obvious_identifier():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("MRN-123456")
