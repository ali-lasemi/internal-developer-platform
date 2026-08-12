from fastapi import APIRouter
from fastapi import HTTPException

from app.models.auth import LoginRequest
from app.models.auth import TokenResponse
from app.models.auth import UserRegistration
from app.security.jwt import create_access_token
from app.security.passwords import hash_password
from app.security.passwords import verify_password


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


users = {}


@router.post(
    "/register",
    status_code=201
)
def register_user(
    request: UserRegistration
):
    if request.username in users:
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )

    users[request.username] = {
        "username": request.username,
        "email": request.email,
        "password": hash_password(
            request.password
        ),
        "team": request.team,
        "role": request.role
    }

    return {
        "username": request.username,
        "email": request.email,
        "team": request.team,
        "role": request.role
    }


@router.post(
    "/token",
    response_model=TokenResponse
)
def login(
    request: LoginRequest
):
    user = users.get(
        request.username
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        request.password,
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        subject=user["username"],
        role=user["role"],
        team=user["team"]
    )

    return TokenResponse(
        access_token=token
    )
