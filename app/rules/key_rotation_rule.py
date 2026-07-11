from app.rules.base import Rule

class KeyRotationRule(Rule):
    id = "IAM-003"
    description = "Rotate access keys every 90 days"
    domain = "IAM"
    THRESHOLD_DAYS = 90

    def evaluate(self, cloud_state: dict) -> list[dict]:
        results = []
        for user in cloud_state.get("iam_users", []):
            age = user.get("access_key_age_days", 0)
            status = "FAIL" if age > self.THRESHOLD_DAYS else "PASS"
            results.append({
                "rule_id": self.id,
                "resource": user["name"],
                "status": status,
                "detail": f"Access key age: {age} days (threshold: {self.THRESHOLD_DAYS})"
            })
        return results