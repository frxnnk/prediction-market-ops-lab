from ops_lab.wallet_verifier import verify_ephemeral_wallet


def test_ephemeral_wallet_proves_control_without_returning_secret_material() -> None:
    result = verify_ephemeral_wallet("prediction-market-ops-lab:local-proof")
    payload = result.model_dump()

    assert result.verified is True
    assert result.address.startswith("0x")
    assert len(result.address) == 42
    assert set(payload) == {"address", "verified"}
    assert "private" not in repr(payload).lower()
    assert "signature" not in repr(payload).lower()
