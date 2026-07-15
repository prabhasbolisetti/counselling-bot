from fastapi import FastAPI

from app.core.config import settings

from app.api.routes.health import router as health_router
from app.api.routes.predictor import router as predictor_router
from app.api.routes.pdf import router as pdf_router
from app.api.routes.webhook import router as webhook_router


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