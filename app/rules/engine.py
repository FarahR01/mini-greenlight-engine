import json

# Important : importer les modules pour déclencher @register_rule
import app.rules.mfa_rule
import app.rules.dormancy_rule
import app.rules.key_rotation_rule
import app.rules.storage_encryption_rule

from app.rules.registry import RULE_REGISTRY
from app.rules.schema import CloudState


def run_engine(cloud_state: dict) -> dict:

    validated = CloudState(**cloud_state)

    cloud_state = validated.model_dump()

    all_results = []

    for rule in RULE_REGISTRY:
        all_results.extend(
            rule.evaluate(cloud_state)
        )


    passed = sum(
        r.status == "PASS"
        for r in all_results
    )

    failed = sum(
        r.status == "FAIL"
        for r in all_results
    )


    risk_score = compute_risk_score(all_results)


    return {
        "risk_score": risk_score,

        "summary": {
            "total": len(all_results),
            "passed": passed,
            "failed": failed,
        },

        "results": [
            r.model_dump()
            for r in all_results
        ],
    }

SEVERITY_WEIGHT = {"CRITICAL": 10, "HIGH": 5, "MEDIUM": 2, "LOW": 1}

def compute_risk_score(results: list) -> float:
    total_weight = sum(SEVERITY_WEIGHT[r.severity] for r in results)
    failed_weight = sum(SEVERITY_WEIGHT[r.severity] for r in results if r.status == "FAIL")
    if total_weight == 0:
        return 100.0
    return round(100 - (failed_weight / total_weight * 100), 1)

if __name__ == "__main__":

    with open("app/rules/schema_example.json") as f:
        state = json.load(f)

    report = run_engine(state)

    print(json.dumps(report, indent=2))