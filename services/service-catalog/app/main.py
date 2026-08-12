from fastapi import FastAPI

from app.routes.catalog import router


app = FastAPI(
    title="Internal Developer Platform Service Catalog",
    description="Persistent service inventory and ownership registry.",
    version="0.3.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "service-catalog",
        "version": "0.3.0"
    }


@app.get("/ready")
def readiness():
    return {
        "status": "ready"
    }


@app.get("/")
def root():
    return {
        "product": "Internal Developer Platform",
        "service": "service-catalog",
        "docs": "/docs",
        "health": "/health"
    }
