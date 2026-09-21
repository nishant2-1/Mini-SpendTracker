# Mini Spend Tracker

Small expense logger with a Python REST API, SQLite, a tiny HTML UI, and a category spend insight.

## How to run

```bash
cd mini-spend-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional; default API key is dev-secret-key
uvicorn app.main:app --reload
```

Open http://localhost:8000 for the UI, or http://localhost:8000/docs for the OpenAPI explorer.

Send `X-API-Key: dev-secret-key` (or whatever you set in `API_KEY`) on API requests:

```bash
curl -X POST http://localhost:8000/expenses \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{"amount": 12.50, "category": "food", "note": "lunch", "date": "2026-09-21"}'

curl http://localhost:8000/summary -H "X-API-Key: dev-secret-key"
```

### Tests

```bash
pytest -q
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/expenses` | Create an expense (`amount`, `category`, `note`, `date`) |
| `GET` | `/expenses` | List expenses. Query: `category`, `from`, `to` |
| `GET` | `/summary` | Total spend, spend by category, month-over-month, insights |
| `GET` | `/health` | Liveness (no API key) |

Validation errors return **422**. Bad date ranges return **400**. Missing/wrong API key returns **401**.

## Key design decisions

- **SQLite + SQLAlchemy** so data survives restarts. An in-memory list would fail the “real database” requirement and make filtering/summary harder to test honestly.
- **Amounts stored as integer cents.** Money in floating point is a classic bug. The API still accepts `12.50`; persistence uses `1250`.
- **Summary math lives in a pure function** (`app/services/summary.py`) so month-over-month and the 20% insight can be tested with fixture rows, not only HTTP.
- **API key via `X-API-Key`.** Enough for a mini take-home without standing up users/passwords. `/` and `/health` stay public so the UI can load.
- **UI is one HTML file** served by the same FastAPI process. That proves end-to-end without a second build toolchain.

Month-over-month uses the **calendar month of today** versus the previous calendar month. A category is flagged when current-month spend is **more than 20% above** last month. If last month was `$0`, percent change is undefined, so we do not flag it.

## Deploy

Render (free web service) is the intended host:

1. Push this repo to GitHub.
2. In Render, create a Web Service from the repo, or use `render.yaml`.
3. Set `API_KEY` in the environment. SQLite on a free instance is ephemeral across deploys; that is noted below.

Dockerfile is included for Fly.io / Railway if you prefer containers:

```bash
fly launch   # if you have flyctl and an account
```

## What I would do with more time

- Real user accounts (JWT) instead of a single shared API key.
- Postgres + migrations (Alembic) so deploys do not wipe SQLite files.
- Pagination, categories as a lookup table, and timezone-aware “month” based on the user’s locale.
- Idempotency keys on `POST /expenses` and request logging.
- Chart the last 6 months and let the summary month be chosen, not only “today”.
