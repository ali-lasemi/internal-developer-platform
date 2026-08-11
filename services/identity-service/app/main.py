from fastapi import FastAPI
from app.routes.identity import router

app = FastAPI(
    title="Identity Service",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "identity-service"
    }
