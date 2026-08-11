from fastapi import FastAPI
from app.routes.services import router

app = FastAPI(
    title="Internal Developer Platform API",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "platform-api"
    }
