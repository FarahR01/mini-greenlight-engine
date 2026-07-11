import yaml
from pathlib import Path

def load_config(path: str = "config/rules.yaml") -> dict:
    with open(Path(path)) as f:
        return yaml.safe_load(f)