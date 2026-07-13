import json

from app.rules.engine import run_engine


def test_engine_handles_azure_provider():
    with open("app/rules/schema_example_azure.json") as f:
        state = json.load(f)

    report = run_engine(state)

    # The engine should evaluate Azure resources using generic rules
    assert report["summary"]["total"] > 0

    # Azure provider should be preserved
    assert report["vendor_name"] == "Acme AI Vendor (Azure)"

    # Both passing and failing checks should be evaluated
    assert report["summary"]["passed"] > 0
    assert report["summary"]["failed"] > 0

    # Provider-agnostic domains should still be evaluated
    assert "IAM" in report["by_domain"]
    assert "Compute" in report["by_domain"]
    assert "Storage" in report["by_domain"]
    assert "Database" in report["by_domain"]

def test_azure_resources_keep_provider_metadata():
    with open("app/rules/schema_example_azure.json") as f:
        state = json.load(f)

    report = run_engine(state)

    assert all(
        resource["cloud_provider"] == "azure"
        for resource in state["compute_instances"]
    )