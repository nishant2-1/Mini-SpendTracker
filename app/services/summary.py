from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from app.money import from_cents
from app.schemas import CategorySpend, Insight, MonthOverMonth, SummaryOut

INSIGHT_THRESHOLD = Decimal("0.20")


def month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


def previous_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def pct_change(current: Decimal, previous: Decimal) -> Decimal | None:
    if previous == 0:
        return None
    return ((current - previous) / previous).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def build_summary(
    rows: list[tuple[str, date, int]],
    today: date,
) -> SummaryOut:
    """rows: (category, occurred_on, amount_cents). Pure function so tests don't need a DB."""
    total_cents = sum(cents for _, _, cents in rows)

    by_category_all: dict[str, int] = defaultdict(int)
    current_by_cat: dict[str, int] = defaultdict(int)
    previous_by_cat: dict[str, int] = defaultdict(int)
    current_total = 0
    previous_total = 0

    prev_year, prev_month = previous_month(today.year, today.month)
    current_start, current_end = month_bounds(today.year, today.month)
    previous_start, previous_end = month_bounds(prev_year, prev_month)

    for category, occurred_on, cents in rows:
        by_category_all[category] += cents
        if current_start <= occurred_on <= current_end:
            current_by_cat[category] += cents
            current_total += cents
        elif previous_start <= occurred_on <= previous_end:
            previous_by_cat[category] += cents
            previous_total += cents

    categories = sorted(set(by_category_all) | set(current_by_cat) | set(previous_by_cat))
    by_category: list[CategorySpend] = []
    insights: list[Insight] = []

    for category in categories:
        current = from_cents(current_by_cat[category])
        previous = from_cents(previous_by_cat[category])
        change = pct_change(current, previous)
        flagged = change is not None and change > INSIGHT_THRESHOLD
        by_category.append(
            CategorySpend(
                category=category,
                total=from_cents(by_category_all[category]),
                current_month=current,
                previous_month=previous,
                month_over_month_pct=None if change is None else (change * 100).quantize(Decimal("0.01")),
                increased_over_20_pct=flagged,
            )
        )
        if flagged and change is not None:
            pct_display = (change * 100).quantize(Decimal("0.01"))
            insights.append(
                Insight(
                    category=category,
                    message=(
                        f"{category} spend is up {pct_display}% versus last month "
                        f"({previous} → {current})."
                    ),
                    current_month=current,
                    previous_month=previous,
                    change_pct=pct_display,
                )
            )

    overall_change = pct_change(from_cents(current_total), from_cents(previous_total))
    summary = SummaryOut(
        total_spend=from_cents(total_cents),
        by_category=by_category,
        month_over_month=MonthOverMonth(
            current_month=f"{today.year:04d}-{today.month:02d}",
            previous_month=f"{prev_year:04d}-{prev_month:02d}",
            current_total=from_cents(current_total),
            previous_total=from_cents(previous_total),
            change_amount=from_cents(current_total - previous_total),
            change_pct=None
            if overall_change is None
            else (overall_change * 100).quantize(Decimal("0.01")),
        ),
        insights=insights,
    )
    return summary
