from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule

@register_rule
class AuditLoggingRule(Rule):
    id = "LOG-001"
    description = "Audit logging must be enabled"
    domain = "Logging"
    severity = Severity.HIGH

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for log in cloud_state.get("logging_configs", []):
            passed = log.get("audit_logging_enabled", False)
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=log["resource_name"],
                status="PASS" if passed else "FAIL",
                detail=f"Audit logging {'enabled' if passed else 'disabled'}",
                remediation="Enable audit logging for this resource." if not passed else ""
            ))
        return results

@register_rule
class IncidentContactRule(Rule):
    id = "LOG-002"
    description = "Incident contact must be configured"
    domain = "Logging"
    severity = Severity.MEDIUM

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for log in cloud_state.get("logging_configs", []):
            passed = log.get("incident_contact_configured", False)
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=log["resource_name"],
                status="PASS" if passed else "FAIL",
                detail=f"Incident contact {'configured' if passed else 'missing'}",
                remediation="Configure primary and backup incident contacts in tenant metadata." if not passed else ""
            ))
        return results