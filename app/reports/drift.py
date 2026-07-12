def compute_drift(old_report: dict, new_report: dict) -> dict:
    old_by_rule = {(r["rule_id"], r["resource"]): r["status"] for r in old_report["results"]}
    new_by_rule = {(r["rule_id"], r["resource"]): r["status"] for r in new_report["results"]}

    improved, regressed, unchanged = [], [], []

    for key, new_status in new_by_rule.items():
        old_status = old_by_rule.get(key)
        if old_status is None:
            continue
        rule_id, resource = key
        if old_status == "FAIL" and new_status == "PASS":
            improved.append({"rule_id": rule_id, "resource": resource, "from": old_status, "to": new_status})
        elif old_status == "PASS" and new_status == "FAIL":
            regressed.append({"rule_id": rule_id, "resource": resource, "from": old_status, "to": new_status})
        else:
            unchanged.append({"rule_id": rule_id, "resource": resource, "status": new_status})

    return {
        "risk_score_delta": round(new_report["risk_score"] - old_report["risk_score"], 1),
        "improved": improved,
        "regressed": regressed,
        "unchanged_count": len(unchanged),
    }