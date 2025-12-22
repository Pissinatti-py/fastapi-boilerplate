from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CurrencyEnum(str, Enum):
    DOLLAR = "USD"
    EURO = "EUR"
    POUND = "GBP"


class DolarServiceResponse(BaseModel):
    currency_price: int = Field(..., description="Currency price in cents")
    currency_name: str = Field(..., description="Currency name")
    currency_kind: str = Field(..., description="Currency code (USD)")
    currency_formatter: str = Field(..., description="Value formatter")


class EuroQuotation(BaseModel):
    currency: str = Field(..., alias="moeda", description="Currency name")
    code: str = Field(..., alias="sigla", description="Currency code (EUR)")
    comercial_value: float = Field(
        ..., alias="valor_comercial", description="Commercial quote value"
    )

    model_config = {"populate_by_name": True}


class EuroServiceResponse(BaseModel):
    quotation: EuroQuotation = Field(..., alias="cotacao")

    model_config = {"populate_by_name": True}


class LibraServiceResponse(BaseModel):
    request_id: str = Field(..., description="Unique request ID")
    callback_response: str = Field(..., description="Registered callback URL")


class LibraWebhookData(BaseModel):
    price: float = Field(..., description="Quote price")
    currency_kind: str = Field(..., description="Currency code (GBP)")
    name: str = Field(..., description="Currency name")


class LibraWebhookRequest(BaseModel):
    request_id: str = Field(..., description="Original request ID")
    data: LibraWebhookData


class QuotationItem(BaseModel):
    currency: str = Field(..., description="Currency name")
    code: str = Field(..., description="Currency code")
    value: float = Field(..., description="Quote value in BRL")


class TopQuotationResponse(BaseModel):
    top_quotation: QuotationItem = Field(..., description="Currency with lowest quote")
    all_quotation: list[QuotationItem] = Field(
        ..., description="List of all queried quotes"
    )
    response_time_ms: float = Field(
        ..., description="Total response time in milliseconds"
    )


class WebhookReceivedResponse(BaseModel):
    status: str = Field(default="received", description="Receipt status")
    request_id: str = Field(..., description="Received request ID")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
