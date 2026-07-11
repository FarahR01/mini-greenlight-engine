# ADR 0002: Use Pydantic models to validate cloud state input

## Status
Accepted

## Context
The rule engine receives untrusted, potentially malformed JSON representing
a cloud state. Silent failures or type errors deep in a rule would be hard
to debug and could produce misleading compliance results.

## Decision
Validate all incoming cloud state data against explicit Pydantic models
(`CloudState`) before any rule evaluation runs.

## Consequences
- (+) Malformed input fails fast with a clear error, not a silent wrong result
- (+) Self-documenting schema (the models ARE the input contract)
- (-) Requires updating the schema whenever a new resource type is added