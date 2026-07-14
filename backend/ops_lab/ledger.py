import sqlite3
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel

from ops_lab.models import PaperIntent


class PaperFillRecord(BaseModel):
    request_id: str
    market_id: str
    outcome: str
    size: Decimal
    limit_price: Decimal
    recorded_at: str


class PaperLedger:
    def __init__(self, database: str | Path) -> None:
        self._database = str(database)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS paper_fills (
                    request_id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL CHECK (mode = 'paper'),
                    market_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    size TEXT NOT NULL,
                    limit_price TEXT NOT NULL,
                    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def record_fill(self, intent: PaperIntent) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO paper_fills (
                    request_id, mode, market_id, outcome, size, limit_price
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    intent.request_id,
                    intent.mode,
                    intent.market_id,
                    intent.outcome,
                    str(intent.size),
                    str(intent.limit_price),
                ),
            )
            return cursor.rowcount == 1

    def list_fills(self, *, limit: int = 100) -> list[PaperFillRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT request_id, market_id, outcome, size, limit_price, recorded_at
                FROM paper_fills
                ORDER BY recorded_at DESC, request_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [PaperFillRecord.model_validate(dict(row)) for row in rows]
