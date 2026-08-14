from fastapi import FastAPI
from app.routes.platform import router as platform_router

from app.routes.services import router as services_router
from app.routes.provision import router as provision_router


app = FastAPI(
    title="Internal Developer Platform API",
    description="Control plane API for developer self-service workflows.",
    version="0.2.0"
)

app.include_router(services_router)
app.include_router(provision_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "platform-api",
        "version": "0.2.0"
    }


@app.get("/")
def root():
    return {
        "product": "Internal Developer Platform",
        "service": "platform-api",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/ready")
def readiness():
    return {
        "status": "ready"
    }


app.include_router(platform_router)