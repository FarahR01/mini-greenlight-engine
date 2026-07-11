from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule


@register_rule
class KeyRotationRule(Rule):

    id = "IAM-003"
    description = "Rotate access keys every 90 days"
    domain = "IAM"
    severity = Severity.MEDIUM

    THRESHOLD_DAYS = 90

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:

        results = []

        for user in cloud_state.get("iam_users", []):

            age = user.get("access_key_age_days", 0)
            passed = age <= self.THRESHOLD_DAYS

            results.append(
                RuleResult(
                    rule_id=self.id,
                    domain=self.domain,
                    severity=self.severity,
                    resource=user["name"],
                    status="PASS" if passed else "FAIL",
                    detail=f"Access key age: {age} days (threshold: {self.THRESHOLD_DAYS})",
                    remediation=""
                    if passed
                    else "Rotate the user's access keys and remove the old keys."
                )
            )

        return results