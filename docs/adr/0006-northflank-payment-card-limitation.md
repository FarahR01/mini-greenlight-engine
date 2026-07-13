# ADR 0006: Northflank deployment blocked by payment card verification

## Status
Accepted (documented limitation)

## Context
Northflank's free "Developer Sandbox" tier requires a valid payment card
for identity verification before allowing addon/service creation, even
though no charges apply while on the free tier. Cards available in
Tunisia were not accepted by Northflank's payment processor during
testing, despite the same cards working with other services (e.g.
CloudAMQP).

## Decision
Document this as an external platform constraint rather than a design
flaw. CloudAMQP (RabbitMQ) was successfully integrated, proving the
architecture and code changes for external managed services work
correctly. Neon.tech is proposed as a card-free alternative for managed
PostgreSQL, keeping the rest of the Northflank-based plan intact for
future execution once a working payment method is available.

## Consequences
- (+) The deployment architecture and code changes remain fully valid
  and documented, ready to execute
- (+) Demonstrates the ability to adapt plans around real-world
  external constraints
- (-) Full live deployment on Northflank specifically is not completed
  by the original deadline
