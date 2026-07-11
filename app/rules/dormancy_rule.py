from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule
from app.rules.config import load_config
CONFIG = load_config()

@register_rule
class DormancyRule(Rule):

    id = "IAM-002"
    description = "Disable dormant accounts after 45 days"
    domain = "IAM"
    severity = Severity.HIGH

    # THRESHOLD_DAYS = 45

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:

        threshold = CONFIG[self.id]["dormancy_threshold_days"]
        results = []

        for user in cloud_state.get("iam_users", []):

            days = user.get("last_login_days_ago", 0)
            passed = days <= threshold

            results.append(
                RuleResult(
                    rule_id=self.id,
                    domain=self.domain,
                    severity=self.severity,
                    resource=user["name"],
                    status="PASS" if passed else "FAIL",
                    detail=f"Last login {days} days ago (threshold: {threshold})",
                    remediation=""
                    if passed
                    else "Disable the account or verify whether it is still required."
                )
            )

        return results