from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional, List, Dict, Any

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    note: Optional[str] = ""
    date: date

    @field_validator("date", mode="before")
    def parse_date(cls, v):
        if isinstance(v, str) and "/" in v:
            parts = v.split("/")
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return v

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    note: Optional[str] = ""
    date: date

    class Config:
        from_attributes = True

ExpenseOut = ExpenseResponse

class CategorySummary(BaseModel):
    category: str
    all_time: float
    this_month: float
    last_month: float
    mom_change: str

class SummaryOut(BaseModel):
    by_category: List[CategorySummary]
