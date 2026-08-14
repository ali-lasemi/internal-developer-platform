from fastapi import FastAPI
from fastapi import HTTPException

from app.routes.portal import router
from app.services.aggregator import platform_status


app = FastAPI(
    title="Developer Portal API",
    description=(
        "Developer-facing aggregation layer for "
        "internal platform capabilities."
    ),
    version="0.4.0"
)

app.include_router(
    router
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "developer-portal-api",
        "version": "0.3.0"
    }


@app.get("/ready")
async def readiness():
    status = await platform_status()

    if status["healthy_services"] == 0:
        raise HTTPException(
            status_code=503,
            detail=status
        )

    return {
        "status": (
            "ready"
            if status["status"] == "healthy"
            else "degraded"
        ),
        "platform": status
    }


@app.get("/")
def root():
    return {
        "product": "Internal Developer Platform",
        "service": "developer-portal-api",
        "portal": "/portal",
        "docs": "/docs"
    }