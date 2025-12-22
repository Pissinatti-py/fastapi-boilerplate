import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.services.quotation.quotation_service import (
    QuotationService,
    QuotationServiceConfig,
)
from src.schemas.quotation import (
    QuotationItem,
    LibraWebhookRequest,
    LibraWebhookData,
)


@pytest.fixture
def config():
    """Test configuration with mocked URL."""
    return QuotationServiceConfig(
        base_url="http://test-service:3000",
        timeout=5.0,
        pound_wait_timeout=2.0,
    )


@pytest.fixture
def service(config):
    """QuotationService instance with test config."""
    return QuotationService(config)


@pytest.fixture
def mock_dollar_response():
    """Mock response for dollar endpoint."""
    return {
        "currency_price": 550,
        "currency_name": "dollar",
        "currency_kind": "USD",
        "currency_formatter": "int",
    }


@pytest.fixture
def mock_euro_response():
    """Mock response for euro endpoint."""
    return {
        "cotacao": {
            "moeda": "EURO",
            "sigla": "EUR",
            "valor_comercial": 6.25,
        }
    }


@pytest.fixture
def mock_pound_response():
    """Mock response for pound endpoint (initial request)."""
    return {
        "request_id": "test-request-123",
        "callback_response": "http://test:8000/webhook",
    }


class TestQuotationServiceConfig:
    """Tests for QuotationServiceConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = QuotationServiceConfig()
        assert config.base_url == "http://quotation-service:3000"
        assert config.timeout == 10.0
        assert config.pound_wait_timeout == 5.0

    def test_custom_values(self, config):
        """Test custom configuration values."""
        assert config.base_url == "http://test-service:3000"
        assert config.timeout == 5.0
        assert config.pound_wait_timeout == 2.0


class TestGetDollar:
    """Tests for _get_dollar method."""

    @pytest.mark.asyncio
    async def test_get_dollar_success(self, service, mock_dollar_response):
        """Test successful dollar quote retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_dollar_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = mock_response

        result = await service._get_dollar(mock_client)

        assert result is not None
        assert isinstance(result, QuotationItem)
        assert result.currency == "Dollar"
        assert result.code == "USD"
        assert result.value == 5.50

    @pytest.mark.asyncio
    async def test_get_dollar_http_error(self, service):
        """Test dollar quote with HTTP error."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=404),
        )

        result = await service._get_dollar(mock_client)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_dollar_connection_error(self, service):
        """Test dollar quote with connection error."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")

        result = await service._get_dollar(mock_client)

        assert result is None


class TestGetEuro:
    """Tests for _get_euro method."""

    @pytest.mark.asyncio
    async def test_get_euro_success(self, service, mock_euro_response):
        """Test successful euro quote retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_euro_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = mock_response

        result = await service._get_euro(mock_client)

        assert result is not None
        assert isinstance(result, QuotationItem)
        assert result.currency == "EURO"
        assert result.code == "EUR"
        assert result.value == 6.25

    @pytest.mark.asyncio
    async def test_get_euro_http_error(self, service):
        """Test euro quote with HTTP error."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500),
        )

        result = await service._get_euro(mock_client)

        assert result is None


class TestReceivePoundWebhook:
    """Tests for receive_pound_webhook method."""

    def test_receive_webhook_known_request(self, service):
        """Test receiving webhook for known request_id."""
        import asyncio

        request_id = "known-request-123"
        event = asyncio.Event()
        service._pound_events[request_id] = event

        webhook_data = LibraWebhookRequest(
            request_id=request_id,
            data=LibraWebhookData(
                price=7.80,
                currency_kind="GBP",
                name="Pound",
            ),
        )

        result = service.receive_pound_webhook(webhook_data)

        assert result is True
        assert request_id in service._pound_responses
        assert event.is_set()

    def test_receive_webhook_unknown_request(self, service):
        """Test receiving webhook for unknown request_id."""
        webhook_data = LibraWebhookRequest(
            request_id="unknown-request-456",
            data=LibraWebhookData(
                price=7.80,
                currency_kind="GBP",
                name="Pound",
            ),
        )

        result = service.receive_pound_webhook(webhook_data)

        assert result is False


class TestGetBestQuote:
    """Tests for get_best_quote method."""

    @pytest.mark.asyncio
    async def test_get_best_quote_without_pound(
        self, service, mock_dollar_response, mock_euro_response
    ):
        """Test getting best quote without pound."""
        with patch.object(
            service,
            "_get_dollar",
            return_value=QuotationItem(currency="Dollar", code="USD", value=5.50),
        ), patch.object(
            service,
            "_get_euro",
            return_value=QuotationItem(currency="EURO", code="EUR", value=6.25),
        ):
            best, all_quotes = await service.get_best_quote(
                callback_base_url="http://test:8000",
                include_pound=False,
            )

            assert best is not None
            assert best.code == "USD"
            assert best.value == 5.50
            assert len(all_quotes) == 2

    @pytest.mark.asyncio
    async def test_get_best_quote_euro_is_best(self, service):
        """Test when euro has the lowest value."""
        with patch.object(
            service,
            "_get_dollar",
            return_value=QuotationItem(currency="Dollar", code="USD", value=7.50),
        ), patch.object(
            service,
            "_get_euro",
            return_value=QuotationItem(currency="EURO", code="EUR", value=5.80),
        ):
            best, all_quotes = await service.get_best_quote(
                callback_base_url="http://test:8000",
                include_pound=False,
            )

            assert best is not None
            assert best.code == "EUR"
            assert best.value == 5.80

    @pytest.mark.asyncio
    async def test_get_best_quote_one_fails(self, service):
        """Test when one currency fetch fails."""
        with patch.object(
            service,
            "_get_dollar",
            return_value=None,
        ), patch.object(
            service,
            "_get_euro",
            return_value=QuotationItem(currency="EURO", code="EUR", value=6.25),
        ):
            best, all_quotes = await service.get_best_quote(
                callback_base_url="http://test:8000",
                include_pound=False,
            )

            assert best is not None
            assert best.code == "EUR"
            assert len(all_quotes) == 1

    @pytest.mark.asyncio
    async def test_get_best_quote_all_fail(self, service):
        """Test when all currency fetches fail."""
        with patch.object(
            service,
            "_get_dollar",
            return_value=None,
        ), patch.object(
            service,
            "_get_euro",
            return_value=None,
        ):
            best, all_quotes = await service.get_best_quote(
                callback_base_url="http://test:8000",
                include_pound=False,
            )

            assert best is None
            assert len(all_quotes) == 0

    @pytest.mark.asyncio
    async def test_get_best_quote_with_pound(self, service):
        """Test getting best quote including pound."""
        with patch.object(
            service,
            "_get_dollar",
            return_value=QuotationItem(currency="Dollar", code="USD", value=5.50),
        ), patch.object(
            service,
            "_get_euro",
            return_value=QuotationItem(currency="EURO", code="EUR", value=6.25),
        ), patch.object(
            service,
            "_get_pound",
            return_value=QuotationItem(currency="Pound", code="GBP", value=4.90),
        ):
            best, all_quotes = await service.get_best_quote(
                callback_base_url="http://test:8000",
                include_pound=True,
            )

            assert best is not None
            assert best.code == "GBP"
            assert best.value == 4.90
            assert len(all_quotes) == 3
