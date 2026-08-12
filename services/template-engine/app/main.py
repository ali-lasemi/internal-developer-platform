from fastapi import FastAPI
from app.routes.templates import router

app = FastAPI(
    title="Template Engine",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "template-engine"
    }


@app.get("/ready")
def readiness():
    return {
        "status": "ready"
    }
