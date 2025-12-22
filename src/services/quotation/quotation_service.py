import asyncio
from dataclasses import dataclass
from typing import Optional

import httpx

from src.schemas.quotation import (
    DolarServiceResponse,
    EuroServiceResponse,
    LibraServiceResponse,
    LibraWebhookRequest,
    QuotationItem,
)
from src.services.logger_service import logger


@dataclass
class QuotationServiceConfig:
    base_url: str = "http://quotation-service:3000"
    timeout: float = 10.0
    pound_wait_timeout: float = 5.0

    @classmethod
    def from_settings(cls) -> "QuotationServiceConfig":
        from src.core.settings import settings

        return cls(
            base_url=settings.COTACAO_SERVICE_URL,
            timeout=settings.COTACAO_TIMEOUT,
            pound_wait_timeout=settings.COTACAO_LIBRA_WAIT_TIMEOUT,
        )


class QuotationService:
    def __init__(self, config: Optional[QuotationServiceConfig] = None):
        self.config = config or QuotationServiceConfig.from_settings()
        self._pound_responses: dict[str, LibraWebhookRequest] = {}
        self._pound_events: dict[str, asyncio.Event] = {}

    async def _get_dollar(self, client: httpx.AsyncClient) -> Optional[QuotationItem]:
        try:
            response = await client.get(f"{self.config.base_url}/cotacao/dolar")
            response.raise_for_status()

            data = DolarServiceResponse(**response.json())
            value = data.currency_price / 100.0

            logger.info(f"Dollar quote obtained: {value}")
            return QuotationItem(
                currency=data.currency_name.capitalize(),
                code=data.currency_kind,
                value=value,
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Dollar quote: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Dollar quote: {e}")
            return None

    async def _get_euro(self, client: httpx.AsyncClient) -> Optional[QuotationItem]:
        try:
            response = await client.get(
                f"{self.config.base_url}/cotacao/euro",
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            data = EuroServiceResponse(**response.json())

            logger.info(f"Euro quote obtained: {data.quotation.comercial_value}")
            return QuotationItem(
                currency=data.quotation.currency,
                code=data.quotation.code,
                value=data.quotation.comercial_value,
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Euro quote: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Euro quote: {e}")
            return None

    async def _get_pound(
        self, client: httpx.AsyncClient, callback_url: str
    ) -> Optional[QuotationItem]:
        try:
            response = await client.get(
                f"{self.config.base_url}/cotacao/libra",
                params={"callback_url": callback_url},
            )
            response.raise_for_status()

            data = LibraServiceResponse(**response.json())
            request_id = data.request_id

            logger.info(f"Pound: Waiting webhook for request_id={request_id}")

            event = asyncio.Event()
            self._pound_events[request_id] = event

            try:
                await asyncio.wait_for(
                    event.wait(), timeout=self.config.pound_wait_timeout
                )

                webhook_data = self._pound_responses.get(request_id)
                if webhook_data:
                    logger.info(f"Pound quote obtained: {webhook_data.data.price}")
                    return QuotationItem(
                        currency=webhook_data.data.name,
                        code=webhook_data.data.currency_kind,
                        value=webhook_data.data.price,
                    )
                return None

            except asyncio.TimeoutError:
                logger.warning(
                    f"Timeout waiting for Pound webhook (request_id={request_id})"
                )
                return None
            finally:
                self._pound_events.pop(request_id, None)
                self._pound_responses.pop(request_id, None)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Pound quote: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Pound quote: {e}")
            return None

    def receive_pound_webhook(self, webhook_data: LibraWebhookRequest) -> bool:
        request_id = webhook_data.request_id

        if request_id in self._pound_events:
            self._pound_responses[request_id] = webhook_data
            self._pound_events[request_id].set()
            logger.info(f"Pound webhook received: request_id={request_id}")
            return True
        else:
            logger.warning(f"Webhook received for unknown request_id: {request_id}")
            return False

    async def get_best_quote(
        self, callback_base_url: str, include_pound: bool = True
    ) -> tuple[Optional[QuotationItem], list[QuotationItem]]:
        """
        Tries to get the best currency quotation among Dollar, Euro, and optionally Pound.

        :param callback_base_url: Base URL for webhook callbacks
        :type callback_base_url: str
        :param include_pound: Whether to include Pound in the quotation request, defaults to True
        :type include_pound: bool, optional
        :return: A tuple containing the best quotation item and a list of all obtained quotations
        :rtype: tuple[Optional[QuotationItem], list[QuotationItem]]
        """
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            tasks = [
                self._get_dollar(client),
                self._get_euro(client),
            ]

            if include_pound:
                callback_url = f"{callback_base_url}/api/v1.0/quotation/webhook/pound"
                tasks.append(self._get_pound(client, callback_url))

            results = await asyncio.gather(*tasks, return_exceptions=True)

        quotes: list[QuotationItem] = []
        for result in results:
            if isinstance(result, QuotationItem):
                quotes.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Exception fetching quote: {result}")

        if not quotes:
            return None, []

        best = min(quotes, key=lambda c: c.value)

        logger.info(f"Best quote: {best.currency} ({best.code}) = {best.value}")
        return best, quotes


_cotacao_service: Optional[QuotationService] = None


def get_quotation_service() -> QuotationService:
    global _cotacao_service
    if _cotacao_service is None:
        _cotacao_service = QuotationService()
    return _cotacao_service


def configure_cotacao_service(config: QuotationServiceConfig) -> None:
    global _cotacao_service
    _cotacao_service = QuotationService(config)
