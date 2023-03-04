from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    DoesNotExistError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)
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

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_exception_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"},
        )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_exception_handler(
        request: Request,
        exc: InvalidTokenError,
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token"},
        )

    @app.exception_handler(TokenExpiredError)
    async def token_expired_exception_handler(
        request: Request,
        exc: TokenExpiredError,
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token expired"},
        )

    @app.exception_handler(DoesNotExistError)
    async def does_not_exist_exception_handler(
        request: Request,
        exc: DoesNotExistError,
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Not found"},
        )

    app.include_router(router=api_router, prefix="/api")

    return app
