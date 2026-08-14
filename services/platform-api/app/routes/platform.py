from fastapi import APIRouter

from app.services.summary import platform_summary


router = APIRouter(
    prefix="/api/v1/platform",
    tags=["platform"]
)


@router.get("/summary")
async def summary():
    return await platform_summary()