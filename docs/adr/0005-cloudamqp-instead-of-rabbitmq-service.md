# ADR 0005: Use CloudAMQP instead of self-hosting RabbitMQ on Northflank

## Status
Accepted

## Context
Northflank's free tier is limited to 2 services and 1 addon. The pipeline
needs 4 components (gateway, worker, RabbitMQ, Postgres). Postgres fits
as the single managed addon, but hosting RabbitMQ as a third service
would exceed the free tier's service limit.

## Decision
Use CloudAMQP's free "Little Lemur" plan as an externally-hosted message
broker, keeping only gateway and worker as Northflank services.

## Consequences
- (+) Stays within free tier limits (2 services + 1 addon)
- (+) Demonstrates composing multiple free-tier providers under budget
  constraints, a realistic startup engineering trade-off
- (-) Adds a third-party dependency and a slightly higher network hop
  for queue operations