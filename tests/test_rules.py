import pytest

from app.rules.mfa_rule import MFARule
from app.rules.dormancy_rule import DormancyRule


@pytest.mark.parametrize(
    "mfa_enabled, expected",
    [
        (True, "PASS"),
        (False, "FAIL"),
    ],
)
def test_mfa_rule(mfa_enabled, expected):

    state = {
        "iam_users": [
            {
                "name": "u1",
                "mfa_enabled": mfa_enabled
            }
        ]
    }

    result = MFARule().evaluate(state)[0]

    assert result.status == expected



def test_engine_handles_empty_state():

    from app.rules.engine import run_engine

    report = run_engine({})

    assert report["summary"]["total"] == 0



@pytest.fixture
def sample_state():

    return {
        "iam_users": [
            {
                "name": "u1",
                "mfa_enabled": False
            }
        ]
    }



def test_mfa_rule_fails_when_disabled(sample_state):

    results = MFARule().evaluate(sample_state)

    assert results[0].status == "FAIL"



def test_dormancy_rule_passes_under_threshold():

    state = {
        "iam_users": [
            {
                "name": "u1",
                "last_login_days_ago": 10
            }
        ]
    }

    results = DormancyRule().evaluate(state)

    assert results[0].status == "PASS"