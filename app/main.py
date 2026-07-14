from fastapi import FastAPI

from app.core.config import settings

from app.api.routes.health import router as health_router
from app.api.routes.predictor import router as predictor_router
from app.api.routes.pdf import router as pdf_router


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)


# Register Routes
app.include_router(health_router)
app.include_router(predictor_router)
app.include_router(pdf_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to EAMCET WhatsApp Bot API"
    }