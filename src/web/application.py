from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    ApplicationError,
    DoesNotExistError,
    ExpiredAccessTokenError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    PermissionDeniedError,
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

    @app.exception_handler(InvalidAccessTokenError)
    async def invalid_token_exception_handler(
        request: Request,
        exc: InvalidAccessTokenError,
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token"},
        )

    @app.exception_handler(ExpiredAccessTokenError)
    async def token_expired_exception_handler(
        request: Request,
        exc: ExpiredAccessTokenError,
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token expired"},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_exception_handler(
        request: Request,
        exc: PermissionDeniedError,
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Permission denied"},
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request,
        exc: ApplicationError,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
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
