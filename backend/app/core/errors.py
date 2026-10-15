"""Consistent JSON error responses.

Every error has the shape ``{"error": {"code", "message", "details"}}``.
Unexpected exceptions return a generic message: no stack traces, file paths
or internal details reach the client.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("churniq")


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: list[str] | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []


class ServiceUnavailable(APIError):
    def __init__(self, message: str):
        super().__init__(503, "service_unavailable", message)


def _body(code: str, message: str, details: list[str] | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or []}}


def _format_validation_error(err: dict) -> str:
    loc = [str(p) for p in err.get("loc", []) if p not in ("body", "query", "path")]
    where = ".".join(loc) if loc else "request"
    return f"{where}: {err.get('msg', 'invalid value')}"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def _api_error(_: Request, exc: APIError):
        return JSONResponse(status_code=exc.status_code, content=_body(exc.code, exc.message, exc.details))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        details = [_format_validation_error(e) for e in exc.errors()]
        return JSONResponse(status_code=422, content=_body("invalid_request", "The request contains invalid values.", details))

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse(status_code=exc.status_code, content=_body("http_error", message))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):
        log.exception("Unhandled error", exc_info=exc)
        return JSONResponse(status_code=500, content=_body("internal_error", "An unexpected error occurred."))
