from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(..., description="Spend amount in major currency units, e.g. 12.50")
    category: str = Field(..., min_length=1, max_length=64)
    note: str | None = Field(default=None, max_length=500)
    date: date

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("amount must be greater than 0")
        quantized = value.quantize(Decimal("0.01"))
        if quantized != value:
            raise ValueError("amount can have at most 2 decimal places")
        return quantized

    @field_validator("category")
    @classmethod
    def category_trimmed(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("category cannot be blank")
        return cleaned


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: str
    note: str | None
    date: date

    @classmethod
    def from_orm_expense(cls, expense) -> "ExpenseOut":
        return cls(
            id=expense.id,
            amount=(Decimal(expense.amount_cents) / Decimal(100)).quantize(Decimal("0.01")),
            category=expense.category,
            note=expense.note,
            date=expense.occurred_on,
        )


class CategorySpend(BaseModel):
    category: str
    total: Decimal
    current_month: Decimal
    previous_month: Decimal
    month_over_month_pct: Decimal | None
    increased_over_20_pct: bool


class MonthOverMonth(BaseModel):
    current_month: str
    previous_month: str
    current_total: Decimal
    previous_total: Decimal
    change_amount: Decimal
    change_pct: Decimal | None


class Insight(BaseModel):
    category: str
    message: str
    current_month: Decimal
    previous_month: Decimal
    change_pct: Decimal


class SummaryOut(BaseModel):
    total_spend: Decimal
    by_category: list[CategorySpend]
    month_over_month: MonthOverMonth
    insights: list[Insight]


class ErrorDetail(BaseModel):
    detail: str
