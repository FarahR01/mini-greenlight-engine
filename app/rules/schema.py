from pydantic import BaseModel, Field


class IAMUser(BaseModel):
    name: str
    mfa_enabled: bool = False
    last_login_days_ago: int = 0
    access_key_age_days: int = 0
    role: str = "user"
    cloud_provider: str = "unknown"  # aws | gcp | azure


class StorageBucket(BaseModel):
    name: str
    encrypted: bool = False
    public_access: bool = False
    cloud_provider: str = "unknown"  # aws | gcp | azure


class ComputeInstance(BaseModel):
    name: str
    runtime: str
    runtime_supported: bool = True
    secure_boot_enabled: bool = False
    https_only: bool = False
    tls_version: str = "1.2"
    cloud_provider: str = "unknown"  # aws | gcp | azure


class NetworkConfig(BaseModel):
    name: str
    ssh_open_to_world: bool = False
    rdp_open_to_world: bool = False
    firewall_default_deny: bool = False
    cloud_provider: str = "unknown"  # aws | gcp | azure


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
    cloud_provider: str = "unknown"  # aws | gcp | azure


class ContainerImage(BaseModel):
    image: str
    scanned_at: str = ""
    vulnerabilities: list[dict] = Field(default_factory=list)


class CloudState(BaseModel):
    vendor_name: str = "Unknown Vendor"
    cloud_provider: str = "unknown"

    iam_users: list[IAMUser] = Field(default_factory=list)
    storage_buckets: list[StorageBucket] = Field(default_factory=list)
    compute_instances: list[ComputeInstance] = Field(default_factory=list)
    network_configs: list[NetworkConfig] = Field(default_factory=list)
    logging_configs: list[LoggingConfig] = Field(default_factory=list)
    databases: list[DatabaseInstance] = Field(default_factory=list)
    container_images: list[ContainerImage] = Field(default_factory=list)