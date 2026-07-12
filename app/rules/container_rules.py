from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule

SEVERITY_TO_ENGINE = {
    "CRITICAL": Severity.CRITICAL,
    "HIGH": Severity.HIGH,
    "MEDIUM": Severity.MEDIUM,
    "LOW": Severity.LOW,
}


@register_rule
class ContainerVulnerabilityRule(Rule):
    id = "CONT-001"
    description = "Container images must have no known CRITICAL/HIGH CVEs"
    domain = "Container"
    severity = Severity.CRITICAL  # default; actual severity is per-finding below

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for image_entry in cloud_state.get("container_images", []):
            image = image_entry["image"]
            vulns = image_entry.get("vulnerabilities", [])

            if not vulns:
                results.append(RuleResult(
                    rule_id=self.id, domain=self.domain, severity=Severity.LOW,
                    resource=image, status="PASS",
                    detail="No known vulnerabilities found.",
                    remediation=""
                ))
                continue

            for vuln in vulns:
                sev = SEVERITY_TO_ENGINE.get(vuln["severity"], Severity.LOW)
                status = "FAIL" if vuln["severity"] in ("CRITICAL", "HIGH") else "PASS"
                fix = (f"Upgrade {vuln['package']} to {vuln['fixed_version']}"
                       if vuln.get("fixed_version") else "No fix available yet — monitor for updates.")
                results.append(RuleResult(
                    rule_id=self.id, domain=self.domain, severity=sev,
                    resource=f"{image}:{vuln['package']}",
                    status=status,
                    detail=f"{vuln['cve_id']} ({vuln['severity']}) — {vuln['title']}",
                    remediation=fix if status == "FAIL" else ""
                ))
        return results