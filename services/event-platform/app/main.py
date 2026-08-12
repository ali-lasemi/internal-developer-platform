from fastapi import FastAPI

from app.adapters.redis_bus import event_bus
from app.routes.events import router


app = FastAPI(
    title="Internal Developer Platform Event Platform",
    description="Domain event gateway for platform capabilities.",
    version="0.2.0"
)

app.include_router(router)


@app.get("/health")
async def health():
    redis_status = "down"

    try:
        if await event_bus.ping():
            redis_status = "ok"

    except Exception:
        redis_status = "down"

    return {
        "status": "ok",
        "service": "event-platform",
        "version": "0.2.0",
        "dependencies": {
            "redis": redis_status
        }
    }


@app.get("/")
def root():
    return {
        "product": "Internal Developer Platform",
        "service": "event-platform",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/ready")
def readiness():
    return {
        "status": "ready"
    }
