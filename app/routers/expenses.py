from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Expense
from app.money import to_cents
from app.schemas import ExpenseCreate, ExpenseOut

router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)) -> ExpenseOut:
    expense = Expense(
        amount_cents=to_cents(payload.amount),
        category=payload.category,
        note=payload.note,
        occurred_on=payload.date,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return ExpenseOut.from_orm_expense(expense)


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    db: Session = Depends(get_db),
    category: str | None = Query(default=None, max_length=64),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
) -> list[ExpenseOut]:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'from' must be on or before 'to'",
        )

    stmt = select(Expense).order_by(Expense.occurred_on.desc(), Expense.id.desc())
    if category:
        stmt = stmt.where(Expense.category == category.strip())
    if date_from:
        stmt = stmt.where(Expense.occurred_on >= date_from)
    if date_to:
        stmt = stmt.where(Expense.occurred_on <= date_to)

    expenses = db.scalars(stmt).all()
    return [ExpenseOut.from_orm_expense(item) for item in expenses]
