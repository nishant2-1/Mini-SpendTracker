def test_missing_api_key_is_rejected(client):
    response = client.get("/summary")
    assert response.status_code == 401


def test_wrong_api_key_is_rejected(client):
    response = client.post(
        "/expenses",
        json={"amount": 5, "category": "food", "date": "2026-09-01"},
        headers={"X-API-Key": "nope"},
    )
    assert response.status_code == 401


def test_health_is_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
