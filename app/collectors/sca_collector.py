import subprocess
import json


class SCACollector:
    """Runs pip-audit against the project's installed dependencies and
    normalizes findings into the rule engine's expected format."""

    def scan_dependencies(self) -> dict:
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True, text=True, timeout=60
            )
        except FileNotFoundError:
            raise RuntimeError("pip-audit not found — install it with: pip install pip-audit")
        except subprocess.TimeoutExpired:
            raise RuntimeError("pip-audit timed out after 60s")

        # pip-audit returns exit code 1 when vulnerabilities are found — that's expected, not a failure
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"pip-audit did not return valid JSON: {result.stderr[:300]}")

    def to_cloud_state_fragment(self) -> dict:
        raw = self.scan_dependencies()
        vulnerabilities = []
        for dep in raw.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                vulnerabilities.append({
                    "cve_id": vuln.get("id", "UNKNOWN"),
                    "package": dep.get("name", "unknown"),
                    "installed_version": dep.get("version", ""),
                    "fixed_version": ", ".join(vuln.get("fix_versions", [])) or "",
                    "severity": "HIGH",  # pip-audit doesn't always give severity; default conservative
                    "title": vuln.get("description", vuln.get("id", ""))[:200],
                })
        return {"container_images": [{
            "image": "python-dependencies",
            "vulnerabilities": vulnerabilities,
        }]}