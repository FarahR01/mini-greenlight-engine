from app.reports.drift import compute_drift

def test_drift_detects_improvement():
    old = {"risk_score": 40.0, "results": [{"rule_id": "IAM-001", "resource": "u1", "status": "FAIL"}]}
    new = {"risk_score": 60.0, "results": [{"rule_id": "IAM-001", "resource": "u1", "status": "PASS"}]}
    drift = compute_drift(old, new)
    assert drift["risk_score_delta"] == 20.0
    assert len(drift["improved"]) == 1
    assert drift["improved"][0]["rule_id"] == "IAM-001"

def test_drift_detects_regression():
    old = {"risk_score": 60.0, "results": [{"rule_id": "STO-001", "resource": "bucket1", "status": "PASS"}]}
    new = {"risk_score": 40.0, "results": [{"rule_id": "STO-001", "resource": "bucket1", "status": "FAIL"}]}
    drift = compute_drift(old, new)
    assert len(drift["regressed"]) == 1

def test_drift_counts_unchanged():
    old = {"risk_score": 50.0, "results": [{"rule_id": "IAM-001", "resource": "u1", "status": "PASS"}]}
    new = {"risk_score": 50.0, "results": [{"rule_id": "IAM-001", "resource": "u1", "status": "PASS"}]}
    drift = compute_drift(old, new)
    assert drift["unchanged_count"] == 1
    assert drift["risk_score_delta"] == 0.0