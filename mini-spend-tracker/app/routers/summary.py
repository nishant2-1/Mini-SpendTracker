from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Expense
from app.schemas import SummaryOut
from app.services.summary import build_summary

router = APIRouter(prefix="/summary", tags=["summary"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)) -> SummaryOut:
    expenses = db.scalars(select(Expense)).all()
    rows = [(e.category, e.occurred_on, e.amount_cents) for e in expenses]
    return build_summary(rows, today=date.today())
