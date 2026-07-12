from pydantic import BaseModel
from typing import Optional

class IAMUser(BaseModel):
    name: str
    mfa_enabled: bool = False
    last_login_days_ago: int = 0
    access_key_age_days: int = 0
    role: str = "user"

class StorageBucket(BaseModel):
    name: str
    encrypted: bool = False
    public_access: bool = False

class ComputeInstance(BaseModel):
    name: str
    runtime: str
    runtime_supported: bool = True
    secure_boot_enabled: bool = False
    https_only: bool = False
    tls_version: str = "1.2"

class NetworkConfig(BaseModel):
    name: str
    ssh_open_to_world: bool = False
    rdp_open_to_world: bool = False
    firewall_default_deny: bool = False

class LoggingConfig(BaseModel):
    resource_name: str
    audit_logging_enabled: bool = False
    log_retention_days: int = 0
    incident_contact_configured: bool = False

class DatabaseInstance(BaseModel):
    name: str
    encrypted_at_rest: bool = False
    publicly_accessible: bool = False
    backup_enabled: bool = False

# Container image representation for container rules like scanning for vulnerabilities
class ContainerImage(BaseModel):
    image: str
    scanned_at: str = ""
    vulnerabilities: list[dict] = []
class CloudState(BaseModel):
    vendor_name: str = "Unknown Vendor"
    cloud_provider: str = "unknown"
    iam_users: list[IAMUser] = []
    storage_buckets: list[StorageBucket] = []
    compute_instances: list[ComputeInstance] = []
    network_configs: list[NetworkConfig] = []
    logging_configs: list[LoggingConfig] = []
    databases: list[DatabaseInstance] = []
    container_images: list[ContainerImage] = [] # This field is for container rules, like Trivy scans