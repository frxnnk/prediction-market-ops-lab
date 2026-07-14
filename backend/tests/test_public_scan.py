from scripts.scan_public_tree import scan_paths


def test_public_scan_accepts_synthetic_documentation(tmp_path) -> None:
    clean = tmp_path / "README.md"
    clean.write_text("Synthetic data only. Live execution is absent.", encoding="utf-8")

    assert scan_paths([clean]) == []


def test_public_scan_finds_secret_material_and_sensitive_filenames(tmp_path) -> None:
    secret = tmp_path / "credentials.txt"
    secret.write_text(
        "-----BEGIN " + "PRIVATE KEY-----\nnot-a-real-key\n-----END PRIVATE KEY-----",
        encoding="utf-8",
    )
    environment = tmp_path / ".env"
    environment.write_text("DEMO_TOKEN=not-real", encoding="utf-8")

    findings = scan_paths([secret, environment])

    assert {finding.kind for finding in findings} == {"secret-pattern", "sensitive-filename"}
