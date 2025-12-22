import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.schemas.quotation import QuotationItem, LibraWebhookData


@pytest.fixture
def client():
    """Synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/api/v1.0/quotation/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "quote"


class TestBestQuoteEndpoint:
    """Tests for /best endpoint."""

    @pytest.mark.asyncio
    async def test_get_best_quote_success(self, async_client):
        """Test successful best quote retrieval."""
        mock_best = QuotationItem(currency="Dollar", code="USD", value=5.50)
        mock_all = [
            QuotationItem(currency="Dollar", code="USD", value=5.50),
            QuotationItem(currency="EURO", code="EUR", value=6.25),
        ]

        with patch(
            "src.api.v1.endpoints.price.get_quotation_service"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_best_quote.return_value = (mock_best, mock_all)
            mock_service.return_value = mock_instance

            response = await async_client.get(
                "/api/v1.0/quotation/best",
                params={"include_pound": False},
            )

            assert response.status_code == 200
            data = response.json()
            assert "top_quotation" in data
            assert data["top_quotation"]["code"] == "USD"
            assert data["top_quotation"]["value"] == 5.50
            assert len(data["all_quotation"]) == 2
            assert "response_time_ms" in data

    @pytest.mark.asyncio
    async def test_get_best_quote_no_quotes_available(self, async_client):
        """Test when no quotes are available."""
        with patch(
            "src.api.v1.endpoints.price.get_quotation_service"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_best_quote.return_value = (None, [])
            mock_service.return_value = mock_instance

            response = await async_client.get(
                "/api/v1.0/quotation/best",
                params={"include_pound": False},
            )

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_best_quote_with_pound_param(self, async_client):
        """Test include_pound parameter is passed correctly."""
        mock_best = QuotationItem(currency="Pound", code="GBP", value=4.90)
        mock_all = [
            QuotationItem(currency="Dollar", code="USD", value=5.50),
            QuotationItem(currency="EURO", code="EUR", value=6.25),
            QuotationItem(currency="Pound", code="GBP", value=4.90),
        ]

        with patch(
            "src.api.v1.endpoints.price.get_quotation_service"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_best_quote.return_value = (mock_best, mock_all)
            mock_service.return_value = mock_instance

            response = await async_client.get(
                "/api/v1.0/quotation/best",
                params={"include_pound": True},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["top_quotation"]["code"] == "GBP"
            assert len(data["all_quotation"]) == 3


class TestWebhookEndpoint:
    """Tests for /webhook/pound endpoint."""

    def test_receive_webhook_success(self, client):
        """Test successful webhook reception."""
        webhook_payload = {
            "request_id": "test-123",
            "data": {
                "price": 7.80,
                "currency_kind": "GBP",
                "name": "Pound",
            },
        }

        with patch(
            "src.api.v1.endpoints.price.get_quotation_service"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.receive_pound_webhook.return_value = True
            mock_service.return_value = mock_instance

            response = client.post(
                "/api/v1.0/quotation/webhook/pound",
                json=webhook_payload,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "received"
            assert data["request_id"] == "test-123"

    def test_receive_webhook_invalid_payload(self, client):
        """Test webhook with invalid payload."""
        invalid_payload = {
            "invalid": "data",
        }

        response = client.post(
            "/api/v1.0/quotation/webhook/pound",
            json=invalid_payload,
        )

        assert response.status_code == 422  # Validation error

    def test_receive_webhook_unknown_request(self, client):
        """Test webhook for unknown request_id."""
        webhook_payload = {
            "request_id": "unknown-456",
            "data": {
                "price": 7.80,
                "currency_kind": "GBP",
                "name": "Pound",
            },
        }

        with patch(
            "src.api.v1.endpoints.price.get_quotation_service"
        ) as mock_service:
            mock_instance = AsyncMock()
            mock_instance.receive_pound_webhook.return_value = False
            mock_service.return_value = mock_instance

            response = client.post(
                "/api/v1.0/quotation/webhook/pound",
                json=webhook_payload,
            )

            # Should still return 200 even if request unknown
            assert response.status_code == 200
