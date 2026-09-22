from datetime import date
from decimal import Decimal

from app.services.summary import build_summary


def test_summary_totals_and_month_over_month(client, auth_headers, monkeypatch):
    import app.routers.summary as summary_router

    monkeypatch.setattr(summary_router, "date", type("D", (), {"today": staticmethod(lambda: date(2026, 9, 21))}))

    payloads = [
        {"amount": 100, "category": "food", "date": "2026-08-15"},
        {"amount": 40, "category": "food", "date": "2026-09-05"},
        {"amount": 200, "category": "rent", "date": "2026-09-01"},
        {"amount": 10, "category": "fun", "date": "2026-07-01"},
    ]
    for payload in payloads:
        assert client.post("/expenses", json=payload, headers=auth_headers).status_code == 201

    response = client.get("/summary", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_spend"] == "350.00"
    assert body["month_over_month"]["current_month"] == "2026-09"
    assert body["month_over_month"]["previous_month"] == "2026-08"
    assert body["month_over_month"]["current_total"] == "240.00"
    assert body["month_over_month"]["previous_total"] == "100.00"
    assert body["month_over_month"]["change_amount"] == "140.00"
    assert body["month_over_month"]["change_pct"] == "140.00"


def test_insight_flags_category_increase_over_20_percent():
    today = date(2026, 9, 21)
    rows = [
        ("food", date(2026, 8, 10), 10000),  # $100 last month
        ("food", date(2026, 9, 5), 13000),  # $130 this month = +30%
        ("rent", date(2026, 8, 1), 200000),
        ("rent", date(2026, 9, 1), 200000),  # unchanged
        ("transport", date(2026, 8, 1), 5000),
        ("transport", date(2026, 9, 1), 5500),  # +10% — should not flag
    ]
    summary = build_summary(rows, today)
    flagged = {item.category for item in summary.insights}
    assert flagged == {"food"}
    food = next(item for item in summary.by_category if item.category == "food")
    assert food.increased_over_20_pct is True
    assert food.month_over_month_pct == Decimal("30.00")


def test_no_insight_when_previous_month_is_zero():
    today = date(2026, 9, 21)
    rows = [("newcat", date(2026, 9, 1), 5000)]
    summary = build_summary(rows, today)
    assert summary.insights == []
    item = summary.by_category[0]
    assert item.month_over_month_pct is None
    assert item.increased_over_20_pct is False
