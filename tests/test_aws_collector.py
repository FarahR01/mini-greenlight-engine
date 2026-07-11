from unittest.mock import patch, MagicMock
from app.collectors.aws_collector import AWSCollector

@patch("boto3.client")
def test_collect_iam_users_detects_no_mfa(mock_boto_client):
    mock_iam = MagicMock()
    mock_iam.list_users.return_value = {"Users": [{"UserName": "test-user"}]}
    mock_iam.list_mfa_devices.return_value = {"MFADevices": []}
    mock_iam.list_access_keys.return_value = {"AccessKeyMetadata": []}
    mock_boto_client.return_value = mock_iam

    collector = AWSCollector()
    users = collector.collect_iam_users()

    assert users[0]["mfa_enabled"] is False