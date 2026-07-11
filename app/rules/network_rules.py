from app.rules.base import Rule, RuleResult, Severity
from app.rules.registry import register_rule

@register_rule
class OpenPortsRule(Rule):
    id = "NET-001"
    description = "SSH/RDP must not be open to the world (0.0.0.0/0)"
    domain = "Networking"
    severity = Severity.CRITICAL

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for net in cloud_state.get("network_configs", []):
            exposed = net.get("ssh_open_to_world") or net.get("rdp_open_to_world")
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=net["name"],
                status="FAIL" if exposed else "PASS",
                detail=f"SSH open: {net.get('ssh_open_to_world')}, RDP open: {net.get('rdp_open_to_world')}",
                remediation="Restrict SSH/RDP access to specific IP ranges or use a bastion/VPN." if exposed else ""
            ))
        return results

@register_rule
class FirewallDefaultDenyRule(Rule):
    id = "NET-002"
    description = "Firewall should default-deny inbound traffic"
    domain = "Networking"
    severity = Severity.HIGH

    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        results = []
        for net in cloud_state.get("network_configs", []):
            passed = net.get("firewall_default_deny", False)
            results.append(RuleResult(
                rule_id=self.id, domain=self.domain, severity=self.severity,
                resource=net["name"],
                status="PASS" if passed else "FAIL",
                detail=f"Default-deny {'enabled' if passed else 'disabled'}",
                remediation="Set firewall default policy to deny, allow explicit rules only." if not passed else ""
            ))
        return results