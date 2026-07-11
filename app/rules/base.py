# Python Library abc --> provide core infra for Abstract Base Classes 

from abc import ABC, abstractmethod

class Rule(ABC):
    id: str
    description: str
    domain: str  # ex: "IAM", "Storage"

    @abstractmethod
    def evaluate(self, cloud_state: dict) -> list[dict]:
        """Retourne une liste de résultats {resource, status, detail}"""
        pass