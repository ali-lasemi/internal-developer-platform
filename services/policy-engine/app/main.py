from fastapi import FastAPI
from app.routes.policies import router

app = FastAPI(
    title="Policy Engine",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "policy-engine"
    }
