from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"


@router.get("/cutoff")
async def get_cutoff_pdf():

    file_path = DATA_DIR / "category_cutoff.pdf"

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Cutoff PDF not found."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="category_cutoff.pdf"
    )


@router.get("/documents")
async def get_documents_pdf():

    file_path = DATA_DIR / "counselling_documents.pdf"

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Documents PDF not found."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="counselling_documents.pdf"
    )