from fastapi import APIRouter
from src.api.v1.endpoints import dnd5, users

api_router = APIRouter()

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    dnd5.router,
    prefix="/dnd5",
    tags=["D&D 5e"],
)
