from fastapi.testclient import TestClient

from fin_agent.api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_get_quote() -> None:
    response = client.get("/api/v1/quotes/aapl")

    assert response.status_code == 200

    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] > 0
    assert "timestamp" in data


def test_batch_quotes() -> None:
    response = client.post(
        "/api/v1/quotes/batch",
        json={"symbols": ["AAPL", "MSFT", "NVDA"]},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 3
    assert len(data["quotes"]) == 3


def test_invalid_symbol() -> None:
    response = client.get("/api/v1/quotes/AAPL@")

    assert response.status_code == 422

    data = response.json()
    assert data["code"] == "HTTP_ERROR"
    assert data["request_id"]
