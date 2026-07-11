# le moteur qui orchestre tout
import json
from app.rules.mfa_rule import MFARule
from app.rules.dormancy_rule import DormancyRule
from app.rules.key_rotation_rule import KeyRotationRule
from app.rules.storage_encryption_rule import StorageEncryptionRule

REGISTERED_RULES = [MFARule(), DormancyRule(), KeyRotationRule(), StorageEncryptionRule()]

def run_engine(cloud_state: dict) -> dict:
    all_results = []
    for rule in REGISTERED_RULES:
        all_results.extend(rule.evaluate(cloud_state))

    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = sum(1 for r in all_results if r["status"] == "FAIL")

    return {
        "summary": {"total": len(all_results), "passed": passed, "failed": failed},
        "results": all_results
    }

if __name__ == "__main__":
    with open("app/rules/schema_example.json") as f:
        state = json.load(f)
    report = run_engine(state)
    print(json.dumps(report, indent=2))