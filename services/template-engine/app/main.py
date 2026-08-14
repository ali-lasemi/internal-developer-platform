from fastapi import FastAPI

from app.routes.templates import router


app = FastAPI(
    title="Internal Developer Platform Template Engine",
    description=(
        "Golden path template registry and "
        "resolution service."
    ),
    version="0.2.0"
)

app.include_router(
    router
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "template-engine",
        "version": "0.2.0"
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
        "service": "template-engine",
        "docs": "/docs",
        "health": "/health"
    }
