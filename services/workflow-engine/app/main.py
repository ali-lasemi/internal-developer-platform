from fastapi import FastAPI
from app.routes.workflows import router

app = FastAPI(
    title="Workflow Engine",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "workflow-engine"
    }
