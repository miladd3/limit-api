from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Debit Card Limit REST API", version="1.0.0")

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_CARD_ID = "CARD-001"


class LimitType(str, Enum):
    pos = "pos"
    atm = "atm"
    ecom = "ecom"


class ChangeLimitRequest(BaseModel):
    limit: int = Field(ge=0)


class CreateTemporaryLimitRequest(BaseModel):
    limit: int = Field(ge=0)
    startDate: str
    endDate: str


def load_json(filename: str) -> dict | list:
    return json.loads((DATA_DIR / filename).read_text())


def save_json(filename: str, data: dict | list) -> None:
    (DATA_DIR / filename).write_text(json.dumps(data, indent=2))


def ensure_card_exists(card_id: str) -> None:
    limits = load_json("limits.json")
    if card_id not in limits:
        raise HTTPException(status_code=404, detail=f"Card not found: {card_id}")


@app.get("/accounts")
def get_payment_instruments() -> dict:
    accounts = load_json("accounts.json")
    limits = load_json("limits.json")
    temp_limits = load_json("temporary_limits.json")

    for account in accounts:
        for card in account["cards"]:
            card_id = card["cardId"]
            card["currentLimits"] = limits.get(card_id, {})
            card["temporaryLimits"] = temp_limits.get(card_id, [])

    return {"accounts": accounts}


@app.get("/cards/default/limits")
def get_current_limits_default() -> dict:
    return get_current_limits(DEFAULT_CARD_ID)


@app.get("/cards/{card_id}/limits")
def get_current_limits(card_id: str) -> dict:
    ensure_card_exists(card_id)
    limits = load_json("limits.json")
    temp_limits = load_json("temporary_limits.json")

    return {
        "cardId": card_id,
        "limits": limits.get(card_id, {}),
        "temporaryLimits": temp_limits.get(card_id, []),
    }


@app.patch("/cards/{card_id}/limits/{limit_type}")
def change_limit(card_id: str, limit_type: LimitType, payload: ChangeLimitRequest) -> dict:
    ensure_card_exists(card_id)

    limits = load_json("limits.json")
    previous_value = limits[card_id][limit_type.value]
    limits[card_id][limit_type.value] = payload.limit
    save_json("limits.json", limits)

    return {
        "cardId": card_id,
        "type": limit_type.value,
        "old": previous_value,
        "new": payload.limit,
    }


@app.post("/cards/{card_id}/temporary-limits/{limit_type}")
def create_temporary_limit(card_id: str, limit_type: LimitType, payload: CreateTemporaryLimitRequest) -> dict:
    ensure_card_exists(card_id)

    temp_limits = load_json("temporary_limits.json")
    created = {
        "type": limit_type.value,
        "limit": payload.limit,
        "startDate": payload.startDate,
        "endDate": payload.endDate,
    }
    temp_limits.setdefault(card_id, []).append(created)
    save_json("temporary_limits.json", temp_limits)

    return {"cardId": card_id, "created": created}
