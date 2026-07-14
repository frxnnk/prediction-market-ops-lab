from eth_account import Account
from eth_account.messages import encode_defunct
from pydantic import BaseModel


class WalletProofResult(BaseModel):
    address: str
    verified: bool


def verify_ephemeral_wallet(challenge: str) -> WalletProofResult:
    """Create, sign with, and discard a local test account without exposing secrets."""
    if not challenge.strip():
        raise ValueError("challenge cannot be empty")

    account = Account.create()
    message = encode_defunct(text=challenge)
    signed_message = account.sign_message(message)
    recovered_address = Account.recover_message(message, signature=signed_message.signature)
    result = WalletProofResult(
        address=account.address,
        verified=recovered_address == account.address,
    )
    del signed_message
    del account
    return result
