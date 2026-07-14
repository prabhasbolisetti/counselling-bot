from fastapi import APIRouter
from app.db.supabase import supabase

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "API is running"
    }


@router.get("/db-test")
async def db_test():
    try:
        response = (
            supabase
            .table("cutoffs")      # <-- Replace with your actual table name
            .select("*")
            .limit(1)
            .execute()
        )

        return {
            "success": True,
            "rows": response.data
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }