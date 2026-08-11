from fastapi import APIRouter
from app.models.identity import Identity

router = APIRouter(
    prefix="/identities",
    tags=["identity"]
)


identities = []


@router.get("")
def list_identities():
    return identities


@router.post("")
def create_identity(identity: Identity):
    identities.append(identity)
    return identity
