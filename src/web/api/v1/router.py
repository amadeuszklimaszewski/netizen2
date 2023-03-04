from fastapi.routing import APIRouter

from src.web.api.v1.routes.user import user_router

api_router = APIRouter(prefix="/v1", tags=["v1"])
api_router.include_router(user_router)
