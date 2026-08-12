from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.identity import router as identity_router


app = FastAPI(
    title="Internal Developer Platform Identity Service",
    description="Persistent authentication and identity capability for the platform.",
    version="0.4.0"
)

app.include_router(
    identity_router
)

app.include_router(
    auth_router
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "identity-service",
        "version": "0.4.0"
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
        "service": "identity-service",
        "docs": "/docs",
        "health": "/health"
    }
