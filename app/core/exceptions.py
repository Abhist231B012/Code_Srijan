from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ModelNotLoadedError(Exception):
    pass


class PredictionError(Exception):
    pass


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP {exc.status_code} on {request.url}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        logger.warning(f"Validation error on {request.url}: {errors}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation failed",
                "details": [
                    {
                        "field": " -> ".join(str(loc) for loc in e["loc"]),
                        "message": e["msg"],
                    }
                    for e in errors
                ],
            },
        )

    @app.exception_handler(ModelNotLoadedError)
    async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError):
        logger.error(f"Model not loaded: {exc}")
        return JSONResponse(
            status_code=503,
            content={"success": False, "error": "ML model is not available. Please contact admin."},
        )

    @app.exception_handler(PredictionError)
    async def prediction_error_handler(request: Request, exc: PredictionError):
        logger.error(f"Prediction error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Prediction failed: {str(exc)}"},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"},
        )