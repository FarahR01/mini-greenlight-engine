from app.rules.base import Rule

class StorageEncryptionRule(Rule):
    id = "STO-001"
    description = "Data at rest must be encrypted"
    domain = "Storage"

    def evaluate(self, cloud_state: dict) -> list[dict]:
        results = []
        for bucket in cloud_state.get("storage_buckets", []):
            status = "PASS" if bucket.get("encrypted") else "FAIL"
            results.append({
                "rule_id": self.id,
                "resource": bucket["name"],
                "status": status,
                "detail": f"Encryption {'enabled' if status == 'PASS' else 'DISABLED'}"
            })
        return results