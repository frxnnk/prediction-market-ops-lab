# Threat model

## Assets

- User trust in the paper-only boundary.
- Local synthetic ledger integrity.
- Availability of the local demonstration environment.
- Privacy of anyone evaluating or running the project.

Real funds, private keys, user wallets, proprietary strategies, and production data are not
assets handled by this system because the corresponding capabilities are intentionally absent.

## Trust boundaries

1. Browser to local FastAPI API.
2. API to local synthetic ledger.
3. Optional API reads to exact public Polymarket hosts.
4. Ephemeral wallet material held only in process memory for a local challenge.

## Threats and controls

| Threat | Control |
|---|---|
| Accidental live execution | Central executor rejects every mode except `paper`; no write client exists |
| Unexpected outbound host | Exact hostname allowlist plus HTTPS-only URLs |
| Unexpected HTTP mutation | Outbound client exposes GET only |
| Secret persistence | Ephemeral accounts; API returns only public address and verification result |
| Sensitive demo artifacts | Synthetic fixtures only; forbidden-content scan in CI |
| Upstream slowness | Five-second timeout and bounded retries for safe failures only |
| Misleading financial claims | No P&L promises, backtests, or real performance metrics |
| Ledger corruption | SQLite transaction boundary and deterministic request identifiers |

## Explicitly absent capabilities

- Order submission and cancellation.
- Token approvals, signing of orders, bridging, deposits, withdrawals, or transfers.
- Environment variables for keys, mnemonics, API credentials, or funder addresses.
- Production database, log, analytics, or user-data ingestion.
- Proprietary or optimized trading strategies.
