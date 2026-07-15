from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/pdf",
    tags=["PDF"],
)

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"


def _get_pdf(file_name: str) -> Path:
    """
    Returns the PDF path.
    Raises 404 if the file does not exist.
    """

    file_path = DATA_DIR / file_name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{file_name} not found.",
        )

    return file_path


@router.get("/cutoff")
async def get_cutoff_pdf():

    file_path = _get_pdf("category_cutoff.pdf")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="category_cutoff.pdf",
    )


@router.get("/documents")
async def get_documents_pdf():

    file_path = _get_pdf("documents.pdf")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="documents.pdf",
    )