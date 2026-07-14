# Provenance

This project is an independent implementation. Its behavior and terminology come from the
public sources below and from original synthetic requirements. No private repository was used
as a code, test, fixture, schema, UI, or documentation source.

## Public technical sources

| Source | Use | License / status |
|---|---|---|
| [Polymarket Gamma market API](https://docs.polymarket.com/api-reference/markets/list-markets) | Read-only market discovery contract | Public documentation |
| [Polymarket CLOB order book API](https://docs.polymarket.com/api-reference/market-data/get-order-book) | Read-only order-book contract | Public documentation |
| FastAPI | HTTP API and generated OpenAPI schema | MIT |
| HTTPX | Bounded outbound HTTP client | BSD-3-Clause |
| eth-account | Local ephemeral wallet challenge signing | MIT |
| React | Operations dashboard | MIT |
| Vite | Frontend build tooling | MIT |

## Dependency policy

- Each runtime dependency must map to a concrete MVP requirement.
- The backend does not depend on a trading SDK because it cannot send, cancel, bridge, transfer,
  or withdraw anything.
- Test and lint dependencies are development-only.
- New dependencies require an update to this file explaining their purpose.

## Data provenance

- Default markets, fills, balances, incidents, and charts are synthetic fixtures created for
  this repository.
- Optional live reads are limited to public market metadata and public order-book data.
- Screenshots must be created from the synthetic mode.
