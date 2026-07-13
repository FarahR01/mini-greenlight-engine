from unittest.mock import patch, MagicMock
from app.collectors.sca_collector import SCACollector

@patch("subprocess.run")
def test_sca_collector_parses_vulnerabilities(mock_run):
    mock_run.return_value = MagicMock(
        stdout='{"dependencies": [{"name": "example-pkg", "version": "1.0", "vulns": [{"id": "PYSEC-2024-1", "fix_versions": ["1.1"], "description": "test vuln"}]}]}',
        returncode=1
    )
    collector = SCACollector()
    fragment = collector.to_cloud_state_fragment()
    assert len(fragment["container_images"][0]["vulnerabilities"]) == 1