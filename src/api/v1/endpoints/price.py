import time

from fastapi import APIRouter, HTTPException, Query, Request

from src.schemas.quotation import (
    ErrorResponse,
    LibraWebhookRequest,
    TopQuotationResponse,
    WebhookReceivedResponse,
)
from src.services.logger_service import logger
from src.services.quotation import get_quotation_service

router = APIRouter()


@router.get(
    "/best",
    response_model=TopQuotationResponse,
    responses={
        200: {"description": "Quote returned successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Returns the best currency quote",
    description="""
    Queries Dollar, Euro and Pound quote services in parallel
    and returns the currency with the lowest value (cheapest to buy).

    **Service behavior:**
    - **Dollar**: Returns immediately
    - **Euro**: May have 1-5 seconds latency
    - **Pound**: Returns via webhook (callback)

    Response is guaranteed in less than 5 seconds.
    """,
)
async def get_best_quote(
    request: Request,
    include_pound: bool = Query(
        default=True,
        description="Include Pound in query (Senior level). False for Mid/Junior level.",
    ),
):
    start_time = time.perf_counter()

    try:
        callback_base_url = "http://quotation_app:8000"
        service = get_quotation_service()
        best, all_quotes = await service.get_best_quote(
            callback_base_url=callback_base_url, include_pound=include_pound
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if best is None:
            raise HTTPException(status_code=500, detail="Could not obtain any quote")

        return TopQuotationResponse(
            top_quotation=best,
            all_quotation=all_quotes,
            response_time_ms=round(elapsed_ms, 2),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching best quote: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post(
    "/webhook/pound",
    response_model=WebhookReceivedResponse,
    summary="Receives Pound quote webhook",
    description="Callback endpoint to receive Pound quote from external service.",
)
async def receive_pound_webhook(webhook_data: LibraWebhookRequest):
    logger.info(f"Webhook received: request_id={webhook_data.request_id}")

    service = get_quotation_service()
    success = service.receive_pound_webhook(webhook_data)
    logger.info("Webhook processing ...")  # TODO save in DB ?

    if not success:
        logger.warning(
            f"Webhook for request_id={webhook_data.request_id} not recognized"
        )

    return WebhookReceivedResponse(
        status="received", request_id=webhook_data.request_id
    )


@router.get(
    "/health",
    summary="Quote service health check",
    description="Checks if the service is running correctly.",
)
async def health_check():
    return {"status": "healthy", "service": "quote"}
