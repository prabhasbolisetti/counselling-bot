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
    Returns the requested PDF.

    Raises:
        HTTPException(404): File not found.
        HTTPException(500): File exists but cannot be served.
    """

    file_path = DATA_DIR / file_name

    # File does not exist
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Requested PDF not found.",
        )

    # Path is not a file
    if not file_path.is_file():
        raise HTTPException(
            status_code=500,
            detail="Invalid PDF resource.",
        )

    # File is not readable
    if not file_path.stat():
        raise HTTPException(
            status_code=500,
            detail="Unable to access PDF.",
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