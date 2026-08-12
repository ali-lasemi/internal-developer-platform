from fastapi import FastAPI

from app.routes.events import router


app = FastAPI(
    title="Internal Developer Platform Event Platform",
    description="Domain event gateway for platform capabilities.",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "event-platform",
        "version": "0.1.0"
    }


@app.get("/")
def root():
    return {
        "product": "Internal Developer Platform",
        "service": "event-platform",
        "docs": "/docs",
        "health": "/health"
    }
