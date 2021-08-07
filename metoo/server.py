from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router
from core.config import settings
from db.redis import init_redis_pool
import logging
logger = logging.getLogger("uvicorn.info")


def create_app() -> FastAPI:
    """
    生成FatAPI对象
    :return:
    """
    app = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # logger.info(settings.BACKEND_CORS_ORIGINS)
    # logger.info(settings.SQLALCHEMY_DATABASE_URI)
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    register_redis(app)

    return app


def register_redis(app: FastAPI) -> None:
    """
    初始化连接
    :param app:
    :return: None
    """

    @app.on_event("startup")
    async def init_connect():
        # 连接redis
        app.state.redis = await init_redis_pool()