from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.user import router as user_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
v1_router.include_router(user_router)

__all__ = ["v1_router"]
