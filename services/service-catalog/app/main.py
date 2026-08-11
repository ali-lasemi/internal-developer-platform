from fastapi import FastAPI
from app.routes.catalog import router

app = FastAPI(
    title="Service Catalog",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "service-catalog"
    }
