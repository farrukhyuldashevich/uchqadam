"""Environment + runtime config."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BOT_DIR = Path(__file__).resolve().parent
load_dotenv(BOT_DIR / ".env")


@dataclass(frozen=True)
class Config:
    bot_token: str
    ops_group_id: int
    merchant_ids: tuple[int, ...]
    store_name: str
    db_path: Path
    delivery_fee: int
    transfer_card: str
    transfer_holder: str

    @property
    def transfer_enabled(self) -> bool:
        return bool(self.transfer_card and self.transfer_holder)

    @classmethod
    def from_env(cls) -> "Config":
        token = os.environ.get("BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

        ops_raw = os.environ.get("OPS_GROUP_ID", "").strip()
        if not ops_raw:
            raise RuntimeError("OPS_GROUP_ID is not set.")
        try:
            ops_group_id = int(ops_raw)
        except ValueError as exc:
            raise RuntimeError(f"OPS_GROUP_ID must be an integer, got {ops_raw!r}") from exc

        merchants_raw = os.environ.get("MERCHANT_IDS", "").strip()
        merchant_ids: tuple[int, ...] = ()
        if merchants_raw:
            merchant_ids = tuple(int(x) for x in merchants_raw.split(",") if x.strip())

        store_name = os.environ.get("STORE_NAME", "Emir Market").strip() or "Emir Market"

        db_path_raw = os.environ.get("DB_PATH", "uchqadam.db").strip()
        db_path = Path(db_path_raw)
        if not db_path.is_absolute():
            db_path = BOT_DIR / db_path

        delivery_raw = os.environ.get("DELIVERY_FEE", "5000").strip() or "5000"
        try:
            delivery_fee = int(delivery_raw)
        except ValueError as exc:
            raise RuntimeError(f"DELIVERY_FEE must be an integer, got {delivery_raw!r}") from exc

        transfer_card = os.environ.get("TRANSFER_CARD", "").strip()
        transfer_holder = os.environ.get("TRANSFER_HOLDER", "").strip()

        return cls(
            bot_token=token,
            ops_group_id=ops_group_id,
            merchant_ids=merchant_ids,
            store_name=store_name,
            db_path=db_path,
            delivery_fee=delivery_fee,
            transfer_card=transfer_card,
            transfer_holder=transfer_holder,
        )
