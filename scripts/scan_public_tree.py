from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    path: Path
    kind: str
    detail: str


_SECRET_PATTERNS = (
    re.compile("BEGIN" + r"\s+(?:RSA\s+|EC\s+)?PRIVATE\s+KEY"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"0x[a-fA-F0-9]{40}"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
)
_SENSITIVE_FILENAMES = frozenset({".env", "id_rsa", "id_ed25519", "wallet.json"})
_SENSITIVE_SUFFIXES = frozenset({".key", ".pem", ".p12", ".pfx", ".sqlite", ".sqlite3"})


def scan_paths(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        if path.name in _SENSITIVE_FILENAMES or path.suffix.lower() in _SENSITIVE_SUFFIXES:
            findings.append(Finding(path, "sensitive-filename", "sensitive file type"))

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(pattern.search(content) for pattern in _SECRET_PATTERNS):
            findings.append(Finding(path, "secret-pattern", "credential-like material"))
    return findings


def tracked_paths() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"])
    return [Path(item.decode("utf-8")) for item in output.split(b"\0") if item]


def main() -> int:
    findings = scan_paths(tracked_paths())
    for finding in findings:
        print(f"{finding.path}: {finding.kind} ({finding.detail})")
    if findings:
        print(f"Public-tree scan failed with {len(findings)} finding(s).")
        return 1
    print("Public-tree scan passed: no credential-like material or sensitive files found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
