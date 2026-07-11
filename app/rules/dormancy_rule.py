from app.rules.base import Rule

class DormancyRule(Rule):
    id = "IAM-002"
    description = "Disable dormant accounts after 45 days"
    domain = "IAM"
    THRESHOLD_DAYS = 45

    def evaluate(self, cloud_state: dict) -> list[dict]:
        results = []
        for user in cloud_state.get("iam_users", []):
            days = user.get("last_login_days_ago", 0)
            status = "FAIL" if days > self.THRESHOLD_DAYS else "PASS"
            results.append({
                "rule_id": self.id,
                "resource": user["name"],
                "status": status,
                "detail": f"Last login {days} days ago (threshold: {self.THRESHOLD_DAYS})"
            })
        return results