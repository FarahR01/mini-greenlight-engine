# Schema for rule configurations

# Pydantic is a lightning-fast Python library for data parsing and validation
from pydantic import BaseModel

class IAMUser(BaseModel):
    name: str
    mfa_enabled: bool = False
    last_login_days_ago: int = 0
    access_key_age_days: int = 0

class StorageBucket(BaseModel):
    name: str
    encrypted: bool = False
    public_access: bool = False

class CloudState(BaseModel):
    iam_users: list[IAMUser] = []
    storage_buckets: list[StorageBucket] = []