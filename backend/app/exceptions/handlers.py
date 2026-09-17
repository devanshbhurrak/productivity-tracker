from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Normalize detail to error format if not already
        detail = exc.detail
        if isinstance(detail, dict) and "error" in detail:
            content = detail
        elif isinstance(detail, dict) and "code" in detail:
            content = {"error": detail}
        elif isinstance(detail, str):
            # Map to code based on status
            code_map = {
                401: "UNAUTHORIZED",
                403: "FORBIDDEN",
                404: "NOT_FOUND",
                409: "CONFLICT",
                400: "BAD_REQUEST",
            }
            code = code_map.get(exc.status_code, "ERROR")
            content = {"error": {"code": code, "message": detail}}
        else:
            content = {"error": {"code": "ERROR", "message": str(detail)}}
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Return 422 with field-level details, ensure JSON serializable
        errors = exc.errors()
        # Convert any non-serializable ctx values (like exception objects) to strings
        serializable_errors = []
        for err in errors:
            new_err = dict(err)
            if "ctx" in new_err and isinstance(new_err["ctx"], dict):
                new_ctx = {}
                for k, v in new_err["ctx"].items():
                    try:
                        # Test if serializable
                        import json
                        json.dumps(v)
                        new_ctx[k] = v
                    except Exception:
                        new_ctx[k] = str(v)
                new_err["ctx"] = new_ctx
            # Ensure input is serializable (convert bytes etc)
            if "input" in new_err:
                try:
                    import json
                    json.dumps(new_err["input"])
                except Exception:
                    new_err["input"] = str(new_err["input"])
            serializable_errors.append(new_err)
        details = {"fields": serializable_errors}
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": "Validation failed", "details": details}},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
        )
