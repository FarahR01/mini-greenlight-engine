from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule

@register_rule
class DatabaseEncryptionRule(Rule):
    id = "DB-001"
    description = "Databases must be encrypted at rest"
    domain = "Database"
    severity = Severity.CRITICAL

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for db in cloud_state.get("databases", []):
            passed = db.get("encrypted_at_rest", False)
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=db["name"],
                status="PASS" if passed else "FAIL",
                detail=f"Encryption at rest {'enabled' if passed else 'disabled'}",
                remediation="Enable encryption at rest for this database." if not passed else ""
            ))
        return results

@register_rule
class DatabasePublicAccessRule(Rule):
    id = "DB-002"
    description = "Databases must not be publicly accessible"
    domain = "Database"
    severity = Severity.CRITICAL

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for db in cloud_state.get("databases", []):
            exposed = db.get("publicly_accessible", False)
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=db["name"],
                status="FAIL" if exposed else "PASS",
                detail=f"Publicly accessible: {exposed}",
                remediation="Restrict database access to VPC-internal traffic only." if exposed else ""
            ))
        return results