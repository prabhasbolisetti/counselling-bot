import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings

from app.api.routes.health import router as health_router
from app.api.routes.predictor import router as predictor_router
from app.api.routes.pdf import router as pdf_router
from app.api.routes.webhook import router as webhook_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    description="AP EAPCET WhatsApp Counselling Bot API",
    version="1.0.0",
)


# Register Routes
app.include_router(health_router)
app.include_router(predictor_router)
app.include_router(pdf_router)
app.include_router(webhook_router)


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Catch unhandled exceptions.
    Prevents exposing internal errors to users.
    """

    logger.exception(
        "Unhandled exception occurred."
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
        },
    )


@app.get(
    "/",
    tags=["Root"],
    summary="API Status",
)
async def root():
    return {
        "message": "Welcome to AP EAPCET WhatsApp Bot API",
        "version": "1.0.0",
        "status": "running",
    }

