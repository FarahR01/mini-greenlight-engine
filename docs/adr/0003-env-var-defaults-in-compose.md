# ADR 0003: Always provide explicit defaults for secrets in docker-compose.yml

## Status
Accepted

## Context
`${VAR}` without a default in docker-compose.yml silently resolves to an
empty string if the variable is missing from .env, rather than failing
the `docker compose up` command. This caused a real incident during
development: Postgres initialized with an empty password while the
application tried to connect with a different one, producing a
misleading "password authentication failed" error that looked like an
application bug rather than a missing config value.

## Decision
Every secret-bearing environment variable in docker-compose.yml must
either have an explicit fallback default (`${VAR:-default}`) for local
development, or the setup docs must make it unmissable that .env must
define it before first run.

## Consequences
- (+) Faster debugging — failures point to config, not app logic
- (+) New contributors get a working local setup on first try
- (-) Requires discipline to keep .env.example in sync with compose
