from typing import Optional, Literal, List
from pydantic import BaseModel

class LatestItem(BaseModel):
    city: str
    location_id: int
    location_name: str
    value: float
    timestamp: str  # ISO

class AlertItem(BaseModel):
    city: str
    tr_exceed_count: int
    who_exceed_count: int
    worst_value: float
    latest_exceed_ts: str
    window: dict

class RankingItem(BaseModel):
    city: str
    avg_pm10: float
    max_pm10: float
    sample_count: int
    window: Optional[dict] = None
