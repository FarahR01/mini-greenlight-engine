# Mini Greenlight Engine

> A miniature, self-built version of an automated cloud security verification pipeline — built to understand, hands-on, the kind of system I'll be working on as Security Software Engineer at Eydle.

![CI](https://github.com/FarahR01/mini-greenlight-engine/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Context

Eydle acts as an independent trust gatekeeper: when an enterprise wants to adopt an AI vendor's tool, Eydle audits the vendor's cloud configuration against the **App Defense Alliance (ADA) Cloud App and Config Specification** and issues a certification decision — the "Greenlight."

That verification pipeline (FastAPI gateway → RabbitMQ queue → parallel Docker workers → rule engine → compliance reports) is exactly what I'll be building and maintaining in the role. Rather than only reading the spec, I rebuilt a small working version of it myself, end to end, to understand the mechanics before day one.

This project implements a subset of the real ADA Cloud Config Profile as an executable rule engine, wraps it in the same asynchronous architecture Eydle uses in production, and produces the same categories of output (JSON telemetry + DOCX compliance report).

**This is not affiliated with or endorsed by Eydle or the App Defense Alliance.** It's an independent learning project built against the publicly available [ADA Cloud App and Config Specification](https://github.com/appdefensealliance/ASA-WG/tree/develop/Cloud%20App%20and%20Config%20Profile).

---

## Architecture

```
        POST /scan
            │
            ▼
   ┌─────────────────┐
   │  FastAPI Gateway │   accepts scan requests, validates input
   └────────┬─────────┘
            │ publishes job
            ▼
   ┌─────────────────┐
   │    RabbitMQ      │   decouples ingestion from processing
   │   (scan_jobs)    │
   └────────┬─────────┘
            │ consumed by
            ▼
   ┌─────────────────┐
   │   Docker Worker  │   runs the ADA rule engine against
   │                  │   the submitted cloud state
   └────────┬─────────┘
            │
            ▼
   ┌─────────────────────────────┐
   │        Rule Engine           │
   │  6 domains · severity-weighted│
   │  risk scoring · 15+ checks    │
   └────────┬─────────────────────┘
            │
            ▼
   ┌─────────────────────────────┐
   │   Reporting Engine            │
   │  results.json + report.docx   │
   └────────────────────────────────┘
```

This mirrors the real pipeline: **Input Gateway → Message Queue → Parallel Workers → Rule Core → Reporting**, just running on a single machine instead of Northflank-managed infrastructure on Azure.

---
## Architecture Decisions

Key architectural decisions are documented as Architecture Decision Records (ADRs) under [`docs/adr/`](docs/adr/).

Current ADRs:

- [ADR 0001 — Use RabbitMQ for asynchronous job processing](docs/adr/0001-use-rabbitmq-over-direct-calls.md)
- [ADR 0002 — Use Pydantic models to validate cloud state input](docs/adr/0002-pydantic-for-input-validation.md)
- [ADR 0003 — Always provide explicit defaults for secrets in docker-compose.yml](docs/adr/0003-env-var-defaults-in-compose.md)
- [ADR 0004 — Always reference GitHub's actual issue number, not a self-chosen title number](docs/adr/0004-github-issue-numbering-gotcha.md)
- [ADR 0005 — Use CloudAMQP instead of self-hosting RabbitMQ on Northflank](docs/adr/0005-cloudamqp-instead-of-rabbitmq-service.md)
- [ADR 0006 — Northflank deployment blocked by payment card verification](docs/adr/0006-northflank-payment-card-limitation.md)

These records capture the reasoning behind major technical decisions, real incidents encountered during development, and the trade-offs involved. They provide historical context so future contributors understand *why* decisions were made — not just *what* was implemented.

---

## What the rule engine checks

Modeled on the ADA Cloud Config Specification's six domains (built on CIS Benchmarks for AWS/GCP/Azure):

| Domain | Example checks implemented |
|---|---|
| **Compute** | Non-deprecated runtimes, HTTPS-only + modern TLS, Secure Boot / vTPM |
| **Identity & Access Management** | MFA on admin accounts, 45-day dormant account detection, 90-day access key rotation |
| **Networking** | SSH/RDP not exposed to `0.0.0.0/0`, firewall default-deny |
| **Storage** | Encryption at rest, no public bucket access |
| **Logging & Monitoring** | Audit logging enabled, incident contact configured |
| **Database Services** | Encryption at rest, no public database exposure |

Each check returns a structured result with a `rule_id`, `severity` (CRITICAL/HIGH/MEDIUM/LOW), pass/fail status, and remediation guidance — feeding into a weighted **risk score (0–100)**, not just a raw pass/fail count.

---

## Stack

| Component | Choice | Why |
|---|---|---|
| API Gateway | FastAPI | Async-native, matches the real Eydle stack |
| Message Queue | RabbitMQ | Decouples ingestion from processing, handles bursts |
| Worker isolation | Docker | Matches the real sandboxed check execution |
| Rule engine | Plain Python + Pydantic | Typed, validated, mirrors "spec → executable code" |
| Config | YAML | Thresholds (dormancy days, key rotation days) are external, not hardcoded |
| Reporting | `python-docx` | Produces the same DOCX compliance report format |
| CLI | Typer | Mirrors the ergonomics of the real `ada-cloud-audit` CLI |
| Tests | Pytest | Parametrized unit tests per rule |
| CI | GitHub Actions | Runs the test suite on every push/PR |

Everything runs on free, local, or free-tier tools only — no cloud spend required.

---

## Project structure

```
mini-greenlight-engine/
├── app/
│   ├── gateway/        # FastAPI app — POST /scan endpoint
│   ├── worker/          # RabbitMQ consumer, runs the engine per job
│   ├── rules/            # The ADA rule engine
│   │   ├── base.py        # Rule + RuleResult + Severity models
│   │   ├── registry.py     # @register_rule auto-registration
│   │   ├── schema.py        # Pydantic models for cloud state input
│   │   ├── engine.py         # Orchestrator + risk scoring
│   │   ├── *_rule(s).py        # One or more rules per domain
│   │   └── schema_example.json # Sample simulated cloud state (input)
│   └── reports/          # DOCX report generation
├── config/
│   └── rules.yaml       # External thresholds (dormancy days, key rotation, etc.)
├── tests/                # Pytest suite
├── .github/workflows/    # CI pipeline
├── docker-compose.yml    # RabbitMQ service
└── results/              # Scan outputs (gitignored)
```

---

## Getting started

### Prerequisites
- Python 3.12+
- Docker Desktop (running)

### 1. Clone and set up the environment

```bash
git clone https://github.com/FarahR01/mini-greenlight-engine.git
cd mini-greenlight-engine
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
```

### 2. Start RabbitMQ

```bash
docker compose up -d
```
Management UI available at `http://localhost:15672` (guest/guest).

### 3. Run the rule engine directly (no queue, fastest way to see it work)

```bash
python -m app.cli scan --input-file app/rules/schema_example.json
```

### 4. Run the full async pipeline

```bash
# Terminal 1 — start the worker
python -m app.worker.consumer

# Terminal 2 — start the API gateway
uvicorn app.gateway.main:app --reload

# Terminal 3 — submit a scan
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d @app/rules/schema_example.json
```
Results land in `results/` as `<job_id>_report.json` and `<job_id>_report.docx`.

### 5. Run the tests

```bash
pytest tests/
```

---

## Sample output

```json
{
  "vendor_name": "Acme AI Vendor",
  "risk_score": 47.1,
  "summary": { "total": 17, "passed": 8, "failed": 9 },
  "by_domain": {
    "IAM": { "passed": 2, "failed": 4 },
    "Compute": { "passed": 2, "failed": 4 },
    "Networking": { "passed": 1, "failed": 1 },
    "Storage": { "passed": 1, "failed": 1 },
    "Logging": { "passed": 0, "failed": 2 },
    "Database": { "passed": 1, "failed": 1 }
  }
}
```
After fixing a subset of failing controls (e.g. enabling MFA, encrypting a bucket) and re-running the scan, the risk score improves — demonstrating the same remediation → revalidation cycle used in real ADA assessments.
---

## Deployment status

The application architecture was fully designed for deployment on Northflank's free tier, constrained to 2 services + 1 managed addon (see [ADR 0005](docs/adr/0005-cloudamqp-instead-of-rabbitmq-service.md)):
- **RabbitMQ**: successfully migrated to [CloudAMQP](https://www.cloudamqp.com/)'s free tier — connection verified end to end, with the gateway and worker running locally against the real external broker
- **PostgreSQL**: Northflank's managed addon requires payment card verification even on the free "Developer Sandbox" tier. Cards available to me in Tunisia were not accepted by Northflank's payment processor (unrelated to the code or architecture — see [ADR 0006](docs/adr/0006-northflank-payment-card-limitation.md)). [Neon.tech](https://neon.tech) (card-free managed Postgres) is identified as a drop-in replacement.
- **Gateway/Worker services**: Dockerfiles are written and ready (`Dockerfile.gateway`, `Dockerfile.worker`); live hosting on Northflank is blocked by the same payment verification requirement.

In short: the integration code for external managed services is written and validated (CloudAMQP works live); only the Northflank-hosted portion is blocked by a platform-side payment verification issue outside my control.
---
## Automated verification

Run the full Tier 1 test suite (Docker health, rule engine, LocalStack,
auth, async pipeline, DOCX report, pytest) with one command:

\```bash
python scripts/run_tier1_checks.py
\```

---
## Known limitation (as of this submission)

The Trivy integration is implemented and unit-tested (see
`tests/test_container_rules.py`), but live scanning depends on
downloading Trivy's vulnerability database from `mirror.gcr.io`, which
was intermittently unreachable from my network during development.
The collector code, rule logic, and test coverage are complete and
verified independently via mocks — only the live network fetch is
currently blocked.
---
## What this project deliberately does NOT do

To be transparent about scope, since this is a learning project, not a production system:
- It does not connect to a real AWS/GCP/Azure account — it evaluates a simulated JSON cloud state (see [why](#context))
- It does not implement the full ADA specification (hundreds of checks) — a representative subset across all 6 domains
- It does not run actual attack simulations ("Fleck Attack Vectors") — that's simulated adversarial testing, out of scope for a solo weekend project
- It is not fully hosted on Northflank — see [Deployment status](#deployment-status) for what was completed and what was blocked
---

## Roadmap (what I'd build next with more time)

### Completed
- [x] LocalStack live AWS collector
- [x] PostgreSQL persistence + scan history
- [x] Compliance drift comparison
- [x] Automated Tier 1 verification script
- [x] Trivy container image vulnerability scanning (live-validated against nginx:latest)
- [x] CloudAMQP integration for RabbitMQ (live-validated)

### Blocked (external constraint, not technical)
- [ ] Full Northflank hosting for gateway + worker services — blocked by payment card verification (see ADR 0006)
- [ ] Managed PostgreSQL — Neon.tech identified as card-free alternative, not yet executed

### Not yet started
- [ ] Add SBOM/CVE cross-referencing for a lightweight SCA layer
- [ ] OWASP ZAP DAST integration against the gateway itself
- [ ] Simple web dashboard for scan history and risk trends
- [ ] Azure domain support (matching the real `ada-cloud-audit` tool's current gap)
---

## Why I built this

This project exists to genuinely understand — not just describe — the system I'll be responsible for building at Eydle: turning a written security specification into automated, executable, auditable checks running on an async, containerized pipeline. Reading the ADA spec explained the *what*; building this explained the *how* and *why* of every architectural decision (queue-based decoupling, containerized isolation, severity-weighted scoring, config-driven thresholds).

---

## Author

**Farah Rihane** — Security Software Engineer @ Eydle (starting July 2026)
[LinkedIn](https://www.linkedin.com) · [GitHub](https://github.com/FarahR01)