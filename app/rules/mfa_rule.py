from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule

@register_rule
class MFARule(Rule):
    id = "IAM-001"
    description = "Require MFA for administrative access"
    domain = "IAM"
    severity = Severity.CRITICAL

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for user in cloud_state.get("iam_users", []):
            passed = user.get("mfa_enabled", False)
            results.append(RuleResult(
                rule_id=self.id,
                domain=self.domain,
                severity=self.severity,
                resource=user["name"],
                status="PASS" if passed else "FAIL",
                detail=f"MFA {'enabled' if passed else 'not enabled'} for {user['name']}",
                remediation="Enable MFA in IAM settings for this user." if not passed else ""
            ))
        return results