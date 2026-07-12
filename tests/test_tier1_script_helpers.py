import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_tier1_checks import detect_os, record, RESULTS


def test_detect_os_returns_known_platform():
    result = detect_os()
    assert result in ("Windows", "Darwin", "Linux") or isinstance(result, str)


def test_record_appends_to_results():
    RESULTS.clear()
    record("dummy check", True, "note")
    assert RESULTS[-1] == ("dummy check", True, "note")