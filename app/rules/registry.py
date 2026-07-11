RULE_REGISTRY = []

def register_rule(cls):
    """Décorateur : toute règle décorée s'ajoute automatiquement au moteur."""
    RULE_REGISTRY.append(cls())
    return cls