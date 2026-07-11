# ADR 0001: Use RabbitMQ for job queuing instead of direct synchronous calls

## Status
Accepted

## Context
The gateway needs to accept scan requests without blocking the client while
the (potentially slow) rule engine runs. High volumes of concurrent scan
requests must not overwhelm the system or block each other.

## Decision
Use RabbitMQ as a message broker between the FastAPI gateway and the worker
processes, rather than calling the rule engine synchronously inside the
request handler.

## Consequences
- (+) Gateway responds immediately (job accepted, not job completed)
- (+) Workers can be scaled horizontally without touching the gateway
- (+) A worker crash doesn't take down the API
- (-) Adds operational complexity (a broker to run and monitor)
- (-) Requires eventual polling or a webhook for the client to get results

## Alternatives considered
- **Direct synchronous call**: simplest, but blocks the client and doesn't
  scale under load — rejected.
- **Celery**: more features (retries, scheduling) but heavier dependency
  footprint for this project's scope — RabbitMQ + a thin custom consumer
  was preferred to keep the architecture legible.