from app.rules.container_rules import ContainerVulnerabilityRule

def test_container_rule_fails_on_critical_cve():
    state = {
        "container_images": [{
            "image": "test:latest",
            "vulnerabilities": [
                {"cve_id": "CVE-2024-0001", "package": "openssl", "installed_version": "1.0",
                 "fixed_version": "1.1", "severity": "CRITICAL", "title": "Test vuln"}
            ]
        }]
    }
    results = ContainerVulnerabilityRule().evaluate(state)
    assert results[0].status == "FAIL"
    assert "openssl" in results[0].resource

def test_container_rule_passes_with_no_vulns():
    state = {"container_images": [{"image": "clean:latest", "vulnerabilities": []}]}
    results = ContainerVulnerabilityRule().evaluate(state)
    assert results[0].status == "PASS"