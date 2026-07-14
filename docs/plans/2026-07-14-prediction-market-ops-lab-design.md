# Prediction Market Ops Lab Design

## Purpose

The lab is a public portfolio artifact showing how a small team can make a financial integration understandable, testable, and operable. It demonstrates public Polymarket market discovery, public CLOB order-book reads, ephemeral wallet proof-of-control, deterministic paper automation, an operational dashboard, observability, and deployment diagnostics. It does not demonstrate or claim profitable trading.

The implementation is independent. Source material is limited to public API documentation, official open-source dependencies, and original synthetic requirements. No private code, strategies, schemas, fixtures, screenshots, configuration, history, brands, users, wallets, operations, or infrastructure may enter the repository.

## Architecture and data flow

The backend is a small FastAPI application. A centralized read-only HTTP client allows only `GET` requests to an explicit Gamma/CLOB host allowlist, applies timeouts, classifies errors, and retries transient failures. Synthetic fixtures are the default data source so the full system works offline. Live public reads are opt-in and never require credentials.

A deterministic demo policy converts synthetic market snapshots into paper intents. The paper executor accepts only `mode=paper`; every other mode raises a hard failure before any side effect. Trades are stored in a local SQLite ledger containing synthetic identifiers only. Ephemeral wallet verification creates a temporary account, signs a fixed challenge locally, verifies the signature, returns only the address and verification result, and discards the key.

The React dashboard consumes the local API and presents the system as an industrial operations console: warm paper background, dark instrument panels, safety-orange state markers, monospaced telemetry, and a visible “LIVE EXECUTION ABSENT” invariant. It shows service health, synthetic market data, paper activity, dependency failures, and a diagnostic timeline.

## Error handling and safety

- External requests use bounded timeouts and retry only timeouts, network errors, and 5xx responses.
- Unexpected schemas fail closed with typed integration errors.
- The backend never logs wallet secrets or signatures.
- There is no authenticated CLOB trading client and no order, cancellation, bridge, withdrawal, or transfer endpoint.
- Failure injection affects only synthetic/read-only dependencies and is resettable.
- Readiness is false when required local components fail; liveness remains independent.

## Verification strategy

Development follows red-green-refactor. Tests first establish the live-execution prohibition, host/method allowlist, retry behavior, schema validation, wallet secret non-disclosure, deterministic paper output, ledger persistence, health semantics, and API contracts. Frontend tests cover safety messaging and operational states. Completion also requires backend lint/tests, frontend typecheck/tests/build, Docker Compose validation, secret scanning, forbidden-name scanning, and a requirement-by-requirement audit.

