from fastapi import APIRouter

from src.api.v1.endpoints import price

api_router = APIRouter()

api_router.include_router(
    price.router,
    prefix="/quotation",
    tags=["quotation"],
)
