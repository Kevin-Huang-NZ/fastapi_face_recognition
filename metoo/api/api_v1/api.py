from fastapi import APIRouter

from api.api_v1.endpoints import items, faces

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(faces.router, prefix="/faces", tags=["faces"])
