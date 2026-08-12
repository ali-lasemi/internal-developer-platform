from fastapi import FastAPI

from app.db.database import Base
from app.db.database import engine
from app.routes.catalog import router


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Internal Developer Platform Service Catalog",
    description="Persistent service inventory and ownership registry.",
    version="0.2.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "service-catalog",
        "version": "0.2.0"
    }


@app.get("/")
def root():
    return {
        "product": "Internal Developer Platform",
        "service": "service-catalog",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/ready")
def readiness():
    return {
        "status": "ready"
    }
