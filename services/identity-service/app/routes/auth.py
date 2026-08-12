from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import UserRecord
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


@router.post(
    "/register",
    status_code=201
)
def register_user(
    request: UserRegistration,
    database: Session = Depends(get_db)
):
    existing_username = (
        database
        .query(UserRecord)
        .filter(
            UserRecord.username == request.username
        )
        .first()
    )

    if existing_username is not None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    existing_email = (
        database
        .query(UserRecord)
        .filter(
            UserRecord.email == str(request.email)
        )
        .first()
    )

    if existing_email is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    user = UserRecord(
        username=request.username,
        email=str(request.email),
        password_hash=hash_password(
            request.password
        ),
        team=request.team,
        role=request.role,
        active=True
    )

    database.add(user)
    database.commit()
    database.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "team": user.team,
        "role": user.role,
        "active": user.active
    }


@router.post(
    "/token",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    database: Session = Depends(get_db)
):
    user = (
        database
        .query(UserRecord)
        .filter(
            UserRecord.username == request.username
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="User account is disabled"
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        subject=user.username,
        role=user.role,
        team=user.team
    )

    return TokenResponse(
        access_token=token
    )
