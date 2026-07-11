from app.rules.base import Rule

class MFARule(Rule):
    id = "IAM-001"
    description = "Require MFA for administrative access"
    domain = "IAM"

    def evaluate(self, cloud_state: dict) -> list[dict]:
        results = []
        for user in cloud_state.get("iam_users", []):
            status = "PASS" if user.get("mfa_enabled") else "FAIL"
            results.append({
                "rule_id": self.id,
                "resource": user["name"],
                "status": status,
                "detail": f"MFA {'enabled' if status == 'PASS' else 'NOT enabled'} for {user['name']}"
            })
        return results