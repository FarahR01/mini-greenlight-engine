from app.rules.mfa_rule import MFARule
from app.rules.dormancy_rule import DormancyRule

def test_mfa_rule_fails_when_disabled():
    state = {"iam_users": [{"name": "u1", "mfa_enabled": False}]}
    results = MFARule().evaluate(state)
    assert results[0]["status"] == "FAIL"

def test_dormancy_rule_passes_under_threshold():
    state = {"iam_users": [{"name": "u1", "last_login_days_ago": 10}]}
    results = DormancyRule().evaluate(state)
    assert results[0]["status"] == "PASS"