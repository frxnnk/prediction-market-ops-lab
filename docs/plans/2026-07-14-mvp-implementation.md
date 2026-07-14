# Prediction Market Ops Lab MVP Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Build an independent public-ready Polymarket operations lab with read-only integrations, ephemeral test wallets, deterministic paper automation, a synthetic dashboard, observability, tests, Docker Compose, and portfolio documentation.

**Architecture:** FastAPI owns all external integration and local simulation behavior. React/Vite renders an industrial operations console from typed API responses. Synthetic data is the default; the only external network capability is allowlisted public GET access to Gamma and CLOB.

**Tech Stack:** Python 3.13, FastAPI, HTTPX, Pydantic, eth-account, SQLite, pytest, Ruff, React 19, TypeScript, Vite, Vitest, Docker Compose, GitHub Actions.

---

### Task 1: Repository and provenance foundation

**Files:**
- Create: `pyproject.toml`
- Create: `backend/ops_lab/__init__.py`
- Create: `docs/PROVENANCE.md`
- Create: `docs/THREAT_MODEL.md`
- Create: `SECURITY.md`

1. Declare minimal runtime and development dependencies with reasons in provenance.
2. Document public sources and the prohibition on private-source reuse.
3. Document assets, trust boundaries, abuse cases, and the absence of live execution.
4. Run `python -m ruff check .` and resolve only foundation issues.
5. Commit the foundation locally.

### Task 2: Hard live-execution boundary

**Files:**
- Test: `backend/tests/test_execution_boundary.py`
- Create: `backend/ops_lab/models.py`
- Create: `backend/ops_lab/paper_executor.py`

1. Write a failing test asserting that paper intents are accepted.
2. Run the test and confirm failure because the executor does not exist.
3. Implement the smallest paper-only executor and rerun to green.
4. Write a failing test asserting any non-paper mode raises `LiveExecutionDisabled` before persistence.
5. Implement the hard failure and rerun the full test file.
6. Commit locally.

### Task 3: Read-only Polymarket HTTP client

**Files:**
- Test: `backend/tests/test_polymarket_client.py`
- Create: `backend/ops_lab/polymarket.py`

1. Write failing tests for allowed Gamma/CLOB GET requests and rejected methods/hosts.
2. Implement an allowlisted client with typed errors and a 5-second timeout.
3. Write failing tests for retry-on-timeout/5xx and no-retry-on-4xx.
4. Implement bounded retry with injectable sleep.
5. Write and satisfy schema-validation tests for market and order-book responses.
6. Commit locally.

### Task 4: Ephemeral wallet proof and synthetic ledger

**Files:**
- Test: `backend/tests/test_wallet_verifier.py`
- Test: `backend/tests/test_ledger.py`
- Create: `backend/ops_lab/wallet_verifier.py`
- Create: `backend/ops_lab/ledger.py`

1. Write a failing proof-of-control test that asserts the private key and signature are absent from the result.
2. Implement ephemeral local signing and recovery.
3. Write failing SQLite persistence/idempotency tests using temporary databases.
4. Implement the minimal ledger with parameterized SQL.
5. Commit locally.

### Task 5: Deterministic policy and API

**Files:**
- Test: `backend/tests/test_demo_policy.py`
- Test: `backend/tests/test_api.py`
- Create: `backend/ops_lab/demo_policy.py`
- Create: `backend/ops_lab/synthetic.py`
- Create: `backend/ops_lab/app.py`

1. Write a failing test for deterministic intent output from a fixed synthetic snapshot.
2. Implement the policy without performance-oriented thresholds.
3. Write failing API tests for overview, markets, paper run, wallet verification, health, readiness, and metrics.
4. Implement routes and dependency wiring.
5. Add failure-injection tests and implementation for synthetic dependencies only.
6. Commit locally.

### Task 6: Industrial operations dashboard

**Files:**
- Create: `dashboard/package.json`
- Create: `dashboard/src/api.ts`
- Create: `dashboard/src/types.ts`
- Test: `dashboard/src/App.test.tsx`
- Create: `dashboard/src/App.tsx`
- Create: `dashboard/src/styles.css`

1. Write failing UI tests for the live-disabled banner, service health, synthetic market cards, and paper activity.
2. Implement a centralized typed API client with cancellation and clear error states.
3. Implement the dashboard with the approved industrial-console visual direction.
4. Run Vitest, TypeScript, and the production build.
5. Commit locally.

### Task 7: Containers, CI, diagnostics, and portfolio package

**Files:**
- Create: `backend/Dockerfile`
- Create: `dashboard/Dockerfile`
- Create: `docker-compose.yml`
- Create: `.github/workflows/ci.yml`
- Create: `docs/ARCHITECTURE.md`
- Create: `docs/RUNBOOK.md`
- Create: `docs/CASE_STUDY.md`
- Modify: `README.md`

1. Add non-root images and health checks.
2. Add CI jobs for backend and frontend verification plus forbidden-content scanning.
3. Document architecture, diagnosis drills, provenance, limitations, and interview narrative.
4. Validate Compose configuration and run the stack locally.
5. Capture only recreated screenshots from synthetic data if needed later.
6. Commit locally.

### Task 8: Completion audit

1. Run all backend tests and Ruff checks.
2. Run all frontend tests, typecheck, and production build.
3. Run Docker Compose config and health verification.
4. Scan tracked files and history for secrets, private names, wallet-like data, internal endpoints, and real operations.
5. Compare every goal requirement to authoritative evidence.
6. Keep the goal active if any requirement is unproven.
7. Do not create a remote, push, deploy, or publish without explicit user confirmation.

