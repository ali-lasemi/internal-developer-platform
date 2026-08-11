from fastapi import FastAPI
from app.routes.portal import router

app = FastAPI(
    title="Developer Portal API",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "developer-portal-api"
    }
