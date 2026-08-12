from fastapi import APIRouter, HTTPException

from app.schemas.provision import (
    ProvisionServiceRequest,
    ProvisionServiceResponse
)
from app.services.provisioning import provision_service


router = APIRouter(
    prefix="/api/v1/provision",
    tags=["provisioning"]
)


@router.post(
    "/services",
    response_model=ProvisionServiceResponse
)
async def create_service(request: ProvisionServiceRequest):
    try:
        return await provision_service(request)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Platform dependency failure: {exc}"
        ) from exc
