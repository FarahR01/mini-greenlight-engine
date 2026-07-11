from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule


@register_rule
class StorageEncryptionRule(Rule):

    id = "STO-001"
    description = "Data at rest must be encrypted"
    domain = "Storage"
    severity = Severity.CRITICAL

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:

        results = []

        for bucket in cloud_state.get("storage_buckets", []):

            encrypted = bucket.get("encrypted", False)

            results.append(
                RuleResult(
                    rule_id=self.id,
                    domain=self.domain,
                    severity=self.severity,
                    resource=bucket["name"],
                    status="PASS" if encrypted else "FAIL",
                    detail=f"Encryption {'enabled' if encrypted else 'disabled'}",
                    remediation=""
                    if encrypted
                    else "Enable encryption at rest for this storage bucket."
                )
            )

        return results