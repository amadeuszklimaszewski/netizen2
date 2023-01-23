from fastapi import FastAPI

from src.web.api.v1.router import api_router


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="netizen",
        version="1.0.0",
        docs_url="/api/docs",
    )

    app.include_router(router=api_router, prefix="/api")

    return app
