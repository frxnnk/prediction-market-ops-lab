# Case study: operating a prediction-market integration safely

## Context

This public lab distills engineering lessons from a private Polymarket side project built with
friends. In that project I worked across wallet onboarding, CLOB integration, automated trading
workflows, paper/production boundaries, operational dashboards, production diagnosis, tests, health
checks, releases, CI/CD, and deployments. The public implementation is new: it does not reuse the
private code, strategy logic, schemas, data, screenshots, infrastructure, brands, or Git history.

## The engineering problem

Prediction-market automation joins several failure-sensitive surfaces: wallet identity, asynchronous
market data, order books, stateful automation, user-facing controls, and systems that may hold funds.
The interesting engineering work is not a claim about returns. It is making boundaries obvious,
failures diagnosable, releases reversible, and unsafe behavior difficult to express.

## What this artifact demonstrates

- A Gamma/CLOB adapter that is structurally read-only and validates upstream schemas.
- An ephemeral local wallet proof that returns no private material or signature.
- A hard paper-only executor plus a second database constraint.
- An intentionally useless strategy: fixed size and outcome selected by synthetic sequence parity.
- Idempotent SQLite recording with deterministic request identifiers.
- Liveness, readiness, diagnostics, metrics, failure injection, and a diagnostic runbook.
- A typed operational dashboard that makes the safety boundary more prominent than activity.
- Non-root containers and CI that tests, scans, validates, and builds without publishing.

## Decisions and trade-offs

| Decision | Why | Trade-off |
|---|---|---|
| Independent implementation | Clean provenance and no inherited private history | More work than deleting files from a copy |
| Synthetic-by-default | Reproducible demo with no production data | Real market changes are not visible by default |
| Exact endpoint allowlist | Prevent authenticated or unrelated reads through the same hosts | Adding a public endpoint requires a reviewed code change |
| No trading SDK | Removes an entire class of accidental writes | Cannot demonstrate real order submission—and intentionally does not |
| SQLite ledger | Auditable and easy to reset locally | Not designed for distributed production scale |
| Visible hard failure | Makes unsafe modes impossible to mistake for paper | No hidden migration path to live execution |

## Evidence map

| Claim | Public evidence |
|---|---|
| Non-paper modes fail before persistence | `test_execution_boundary.py` and executor guard |
| Public Polymarket reads are constrained | Client allowlist/retry/schema tests and optional API routes |
| Wallet material is not returned | Wallet proof contract test |
| Automation is deterministic and non-proprietary | Dummy policy tests and synthetic fixtures |
| Duplicate runs do not duplicate fills | Ledger idempotency tests and database primary key |
| Operators can distinguish alive from ready | API failure-injection tests and runbook drill |
| Release artifact is reproducible | Lockfile, Dockerfiles, Compose, and CI image builds |

## Explicit limitations

This is not a production trading system, security audit, strategy sample, backtest, or profitability
report. It has no real orders, funds, users, credentials, or production telemetry. Optional public
reads depend on Polymarket's public APIs and are isolated from the synthetic default experience.

## Reusable narrative

### CV

Built and operated a Polymarket side project with friends across wallet/CLOB integration, trading
automation, paper-production safety boundaries, operational dashboards, observability, CI/CD, and
production diagnostics; created an independent paper-only public lab to demonstrate the architecture
without exposing strategies, credentials, users, or financial data.

### LinkedIn

I turned lessons from a private prediction-market side project into a clean public operations lab.
The focus is reliability rather than returns: allowlisted Gamma/CLOB reads, ephemeral wallet proof,
a hard paper-only boundary, deterministic synthetic automation, health/readiness diagnostics, a typed
dashboard, and reproducible containers. No proprietary strategy or production data is included.

### Portfolio

An independent, safety-first prediction-market operations reference. It shows how I structure an
external API integration, make paper/live boundaries enforceable, instrument stateful automation,
and give operators useful diagnostics. The demo is synthetic by default and deliberately lacks every
capability required to submit orders or move funds.

### Interview answer

“The hardest part was not calling an API; it was controlling the blast radius. I treated paper mode
as an invariant across the request contract, executor, and database, then made liveness, readiness,
and diagnostic state independently observable. For the public artifact I reimplemented only generic
patterns from public documentation, kept market reads opt-in, and removed the write-capable dependency
surface entirely. That let me discuss real operational trade-offs without publishing strategy or
production information.”
