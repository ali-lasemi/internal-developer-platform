from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.schemas.provision import ProvisionServiceRequest
from app.schemas.provision import ProvisionServiceResponse
from app.security.auth import require_roles
from app.services.provisioning import provision_service


router = APIRouter(
    prefix="/api/v1/provision",
    tags=["provisioning"]
)


@router.post(
    "/services",
    response_model=ProvisionServiceResponse
)
async def create_service(
    request: ProvisionServiceRequest,
    identity=Depends(
        require_roles(
            "developer",
            "platform-engineer",
            "admin"
        )
    )
):
    try:
        return await provision_service(
            request
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Platform dependency failure: {exc}"
        ) from exc
