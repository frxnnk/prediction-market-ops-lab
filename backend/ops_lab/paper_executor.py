from typing import Protocol

from ops_lab.models import PaperExecutionResult, PaperIntent


class LiveExecutionDisabled(RuntimeError):
    """Raised before side effects when an intent is not explicitly paper-only."""


class FillLedger(Protocol):
    def record_fill(self, intent: PaperIntent) -> None: ...


class PaperExecutor:
    def __init__(self, ledger: FillLedger) -> None:
        self._ledger = ledger

    def execute(self, intent: PaperIntent) -> PaperExecutionResult:
        if intent.mode != "paper":
            raise LiveExecutionDisabled("This lab is paper-only; live execution is disabled")

        self._ledger.record_fill(intent)
        return PaperExecutionResult(request_id=intent.request_id, status="simulated")
