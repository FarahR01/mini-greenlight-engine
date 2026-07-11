# Python Library abc --> provide core infra for Abstract Base Classes 

from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RuleResult(BaseModel):
    rule_id: str
    domain: str
    severity: Severity
    resource: str
    status: str  # PASS | FAIL
    detail: str
    remediation: str

class Rule(ABC):
    id: str
    description: str
    domain: str
    severity: Severity

    @abstractmethod
    def evaluate(self, cloud_state: dict) -> list[RuleResult]:
        ...