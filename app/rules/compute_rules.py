from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule

@register_rule
class RuntimeLifecycleRule(Rule):
    id = "COMP-001"
    description = "Ensure current, non-deprecated runtimes"
    domain = "Compute"
    severity = Severity.HIGH

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for instance in cloud_state.get("compute_instances", []):
            passed = instance.get("runtime_supported", False)
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=instance["name"],
                status="PASS" if passed else "FAIL",
                detail=f"Runtime '{instance['runtime']}' {'supported' if passed else 'deprecated'}",
                remediation="Upgrade to a current, supported runtime version." if not passed else ""
            ))
        return results

@register_rule
class TransitEncryptionRule(Rule):
    id = "COMP-002"
    description = "Enforce HTTPS and disable outdated TLS versions"
    domain = "Compute"
    severity = Severity.CRITICAL

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for instance in cloud_state.get("compute_instances", []):
            https_ok = instance.get("https_only", False)
            tls_ok = instance.get("tls_version", "1.0") not in ["1.0", "1.1"]
            passed = https_ok and tls_ok
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=instance["name"],
                status="PASS" if passed else "FAIL",
                detail=f"HTTPS-only: {https_ok}, TLS: {instance.get('tls_version')}",
                remediation="Force HTTPS and disable TLS 1.0/1.1." if not passed else ""
            ))
        return results

@register_rule
class SecureBootRule(Rule):
    id = "COMP-003"
    description = "Enable Secure Boot / vTPM for asset integrity"
    domain = "Compute"
    severity = Severity.MEDIUM

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for instance in cloud_state.get("compute_instances", []):
            passed = instance.get("secure_boot_enabled", False)
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=instance["name"],
                status="PASS" if passed else "FAIL",
                detail=f"Secure Boot {'enabled' if passed else 'disabled'}",
                remediation="Enable Secure Boot and vTPM on this instance." if not passed else ""
            ))
        return results