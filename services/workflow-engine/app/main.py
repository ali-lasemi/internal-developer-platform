import os

import httpx
from fastapi import FastAPI
from fastapi import HTTPException
from sqlalchemy import text

from app.db.database import engine
from app.routes.workflows import router


EVENT_PLATFORM_URL = os.getenv(
    "EVENT_PLATFORM_URL",
    "http://event-platform:8000"
)


app = FastAPI(
    title="Workflow Engine",
    version="0.4.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "workflow-engine",
        "version": "0.4.0"
    }


@app.get("/ready")
def readiness():
    checks = {
        "database": False,
        "event_platform": False
    }

    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        checks["database"] = True

    except Exception:
        pass

    try:
        response = httpx.get(
            f"{EVENT_PLATFORM_URL}/health",
            timeout=2.0
        )

        checks["event_platform"] = (
            response.status_code == 200
        )

    except Exception:
        pass

    if not all(
        checks.values()
    ):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "checks": checks
            }
        )

    return {
        "status": "ready",
        "checks": checks
    }