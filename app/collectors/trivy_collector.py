import subprocess
import json
from datetime import datetime


class TrivyCollector:
    """Runs a Trivy vulnerability scan against a container image via Docker,
    and normalizes the findings into a format the rule engine can consume."""

    SEVERITY_MAP = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
        "UNKNOWN": "LOW",
    }

    def scan_image(self, image: str, timeout: int = 600) -> dict:
        """timeout par défaut relevé à 600s (10 min) pour le premier téléchargement de la DB Trivy."""
        cmd = [
            "docker", "run", "--rm",
            "-v", "trivy-cache:/root/.cache/",
            "aquasec/trivy", "image", image,
            "--format", "json", "--quiet",
            "--severity", "CRITICAL,HIGH,MEDIUM,LOW",
            "--timeout", "9m",
        ]
        print(f"Running Trivy scan on {image} (this can take several minutes on first run)...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except FileNotFoundError:
            raise RuntimeError("Docker not found — Trivy runs via a Docker image, Docker must be installed and running.")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Trivy scan of '{image}' timed out after {timeout}s (Python-side timeout).")

        if result.returncode != 0:
            raise RuntimeError(f"Trivy scan failed (exit code {result.returncode}): {result.stderr[:800]}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"Trivy did not return valid JSON. stdout: {result.stdout[:300]} | stderr: {result.stderr[:300]}")
    def to_cloud_state_fragment(self, image: str) -> dict:
        """Converts a Trivy scan into a list of 'container_images' entries
        the rule engine can evaluate, one entry per found CVE."""
        raw = self.scan_image(image)
        vulnerabilities = []

        for result in raw.get("Results", []):
            for vuln in result.get("Vulnerabilities", []) or []:
                vulnerabilities.append({
                    "cve_id": vuln.get("VulnerabilityID", "UNKNOWN"),
                    "package": vuln.get("PkgName", "unknown"),
                    "installed_version": vuln.get("InstalledVersion", ""),
                    "fixed_version": vuln.get("FixedVersion", ""),
                    "severity": self.SEVERITY_MAP.get(vuln.get("Severity", "UNKNOWN"), "LOW"),
                    "title": vuln.get("Title", vuln.get("VulnerabilityID", "")),
                })

        return {
            "container_images": [{
                "image": image,
                "scanned_at": datetime.utcnow().isoformat(),
                "vulnerabilities": vulnerabilities,
            }]
        }