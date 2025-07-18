from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class Ticker(BaseModel):
    symbol: str
    timestamp: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    bid_volume: Optional[float] = Field(None, alias="bidVolume")
    ask_volume: Optional[float] = Field(None, alias="askVolume")

    class Config:
        populate_by_name = True


class BalanceAsset(BaseModel):
    asset: str
    free: float
    used: float
    total: float


class Balance(BaseModel):
    timestamp: int
    assets: List[BalanceAsset]


class Order(BaseModel):
    id: str = Field(alias="oid")
    symbol: str
    side: str
    type: str
    status: str
    price: float | None = None
    amount: float
    filled: float
    remaining: float
    cost: float | None = None
    created_at: int
    updated_at: int | None = None

    class Config:
        allow_population_by_field_name = True
