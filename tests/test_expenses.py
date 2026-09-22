def test_create_expense(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 12.5, "category": "food", "note": "lunch", "date": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["amount"] == "12.50"
    assert body["category"] == "food"
    assert body["note"] == "lunch"
    assert body["date"] == "2026-09-01"


def test_reject_zero_and_negative_amount(client, auth_headers):
    for amount in (0, -3):
        response = client.post(
            "/expenses",
            json={"amount": amount, "category": "food", "date": "2026-09-01"},
            headers=auth_headers,
        )
        assert response.status_code == 422


def test_reject_too_many_decimals(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 1.234, "category": "food", "date": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_reject_blank_category(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"amount": 5, "category": "   ", "date": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_filters_by_category_and_date_range(client, auth_headers):
    payloads = [
        {"amount": 10, "category": "food", "date": "2026-08-01"},
        {"amount": 20, "category": "food", "date": "2026-09-10"},
        {"amount": 30, "category": "rent", "date": "2026-09-10"},
    ]
    for payload in payloads:
        created = client.post("/expenses", json=payload, headers=auth_headers)
        assert created.status_code == 201

    food = client.get("/expenses", params={"category": "food"}, headers=auth_headers)
    assert {item["amount"] for item in food.json()} == {"10.00", "20.00"}

    september = client.get(
        "/expenses",
        params={"from": "2026-09-01", "to": "2026-09-30"},
        headers=auth_headers,
    )
    assert {item["category"] for item in september.json()} == {"food", "rent"}
    assert len(september.json()) == 2


def test_invalid_date_range_returns_400(client, auth_headers):
    response = client.get(
        "/expenses",
        params={"from": "2026-09-30", "to": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "from" in response.json()["detail"]
