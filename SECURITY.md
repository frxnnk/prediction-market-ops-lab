# Security policy

## Safety invariant

This repository is paper-only. It must not contain a code path that submits or cancels an order,
moves funds, approves tokens, or persists a private key. Any change that weakens this invariant is
a security-sensitive change and should be rejected.

## Secrets

The application does not require secrets. Do not add private keys, mnemonics, API credentials,
wallet databases, production endpoints, real user data, or copied logs. If a secret is found in
history, revoke it first and report it privately before attempting repository cleanup.

## Reporting

Please report a suspected vulnerability privately to the repository owner with reproduction steps
and impact. Do not include active credentials or personal data in the report.
