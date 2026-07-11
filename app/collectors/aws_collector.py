import boto3
from datetime import datetime, timezone

import os
from dotenv import load_dotenv

load_dotenv()


class AWSCollector:
    """Collects cloud state from AWS-compatible endpoints."""

    def __init__(self, endpoint_url: str | None = None):

        self._session_kwargs = {
            "endpoint_url": endpoint_url or os.getenv(
                "AWS_ENDPOINT_URL"
            ),
            "aws_access_key_id": os.getenv(
                "AWS_ACCESS_KEY_ID"
            ),
            "aws_secret_access_key": os.getenv(
                "AWS_SECRET_ACCESS_KEY"
            ),
            "region_name": os.getenv(
                "AWS_DEFAULT_REGION",
                "us-east-1"
            ),
        }
    def collect_iam_users(self) -> list[dict]:
        iam = boto3.client("iam", **self._session_kwargs)
        users = iam.list_users().get("Users", [])
        results = []
        for u in users:
            mfa_devices = iam.list_mfa_devices(UserName=u["UserName"]).get("MFADevices", [])
            access_keys = iam.list_access_keys(UserName=u["UserName"]).get("AccessKeyMetadata", [])
            key_age_days = 0
            if access_keys:
                key_age_days = max(
                    (
                    datetime.now(timezone.utc) - key["CreateDate"]
                    ).days
                    for key in access_keys
                )
                created = access_keys[0]["CreateDate"]
                key_age_days = (datetime.now(timezone.utc) - created).days
            last_used = u.get("PasswordLastUsed")
            last_login_days = (datetime.now(timezone.utc) - last_used).days if last_used else 999
            results.append({
                "name": u["UserName"],
                "mfa_enabled": len(mfa_devices) > 0,
                "last_login_days_ago": last_login_days,
                "access_key_age_days": key_age_days,
                "role": "user",
            })
        return results

    def collect_storage_buckets(self) -> list[dict]:
        s3 = boto3.client("s3", **self._session_kwargs)
        buckets = s3.list_buckets().get("Buckets", [])
        results = []
        for b in buckets:
            name = b["Name"]
            encrypted = False
            try:
                s3.get_bucket_encryption(Bucket=name)
                encrypted = True
            except s3.exceptions.ClientError:
                encrypted = False
            public = False
            try:
                acl = s3.get_bucket_acl(Bucket=name)
                public = any("AllUsers" in str(g.get("Grantee", {})) for g in acl.get("Grants", []))
            except Exception:
                pass
            results.append({"name": name, "encrypted": encrypted, "public_access": public})
        return results

    def collect_all(self, vendor_name: str = "LocalStack Vendor") -> dict:
        return {
            "vendor_name": vendor_name,
            "cloud_provider": "aws-localstack",
            "iam_users": self.collect_iam_users(),
            "storage_buckets": self.collect_storage_buckets(),
        }