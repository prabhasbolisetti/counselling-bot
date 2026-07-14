from fastapi import APIRouter

from app.schemas.predictor import PredictorRequest
from app.services.predictor_service import predict_colleges

router = APIRouter(
    prefix="/predict",
    tags=["College Predictor"]
)


@router.post("")
async def predictor(request: PredictorRequest):

    results = await predict_colleges(
        rank=request.rank,
        category=request.category,
        gender=request.gender,
    )

    return {
        "success": True,
        "count": len(results),
        "results": results
    }