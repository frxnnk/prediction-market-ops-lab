# Operations runbook

This runbook is for the local synthetic demonstration. It does not contain a procedure for enabling
real trading because that capability is absent.

## Start and verify

```bash
docker compose up --build -d
docker compose ps
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
curl --fail http://127.0.0.1:8000/api/diagnostics
curl --fail http://127.0.0.1:8000/metrics
```

Open `http://127.0.0.1:5173`. Expected state:

- `LIVE EXECUTION ABSENT` is the first banner.
- Runtime mode is `PAPER / SYNTHETIC`.
- Readiness and the four diagnostic cells are nominal.
- Running the cycle adds one simulated event and one idempotent ledger row.

## Health semantics

- `/healthz`: the HTTP process can answer. It stays `200` during a dependency drill.
- `/readyz`: required synthetic inputs are available. It becomes `503` when they are injected down.
- `/api/diagnostics`: human-readable boundary, fixture, ledger, and outbound status.
- `/metrics`: small Prometheus-compatible counters and the always-zero live execution gauge.

## Failure drill: synthetic provider unavailable

PowerShell:

```powershell
$env:OPS_LAB_SYNTHETIC_AVAILABLE = "0"
docker compose up -d --force-recreate backend
curl.exe http://127.0.0.1:8000/healthz
curl.exe -i http://127.0.0.1:8000/readyz
```

Expected result: liveness is `200`; readiness is `503` with dependency `synthetic_data`. Restore:

```powershell
$env:OPS_LAB_SYNTHETIC_AVAILABLE = "1"
docker compose up -d --force-recreate backend
```

## Optional public read-only smoke test

Public reads are disabled by default and require no secret:

```powershell
$env:OPS_LAB_PUBLIC_READS = "1"
docker compose up -d --force-recreate backend
curl.exe "http://127.0.0.1:8000/api/public/markets?limit=1"
```

Take a `clob_token_ids` value returned by that endpoint and request the public book:

```powershell
curl.exe "http://127.0.0.1:8000/api/public/order-book/TOKEN_ID"
```

Turn the flag back to `0` after the smoke test. A `403` when disabled is expected. A `502` means the
public upstream failed or returned a schema the adapter rejected; inspect the backend logs without
printing full payloads.

## Diagnosis sequence

1. Run `docker compose ps` and distinguish container state from application readiness.
2. Check `/healthz`, then `/readyz`, then `/api/diagnostics`.
3. Inspect bounded logs: `docker compose logs --tail 100 backend dashboard`.
4. Confirm `OPS_LAB_SYNTHETIC_AVAILABLE=1` and, unless needed, `OPS_LAB_PUBLIC_READS=0`.
5. Validate the configuration with `docker compose config --quiet`.
6. Re-run backend tests and the public-tree scan before changing code.

## Stop and reset

```bash
docker compose down
```

The named volume preserves only synthetic paper fills. To remove it deliberately:

```bash
docker compose down --volumes
```

Never point the volume at an existing wallet, bot, database, or log directory.

## Release checklist

1. Backend: Ruff, pytest, and public-tree scan green.
2. Dashboard: Vitest, TypeScript, and production build green.
3. Compose config valid; both images build from a clean checkout.
4. Containers healthy; paper cycle works through the dashboard proxy.
5. Synthetic-failure drill produces the documented liveness/readiness split.
6. Optional public reads remain disabled in the default configuration.
7. No remote, image push, deployment, or publication occurs without an explicit release decision.
