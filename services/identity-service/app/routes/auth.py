from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Header
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import UserRecord
from app.models.auth import LoginRequest
from app.models.auth import UserRegistration
from app.models.session import LogoutRequest
from app.models.session import RefreshRequest
from app.models.session import SessionTokenResponse
from app.security.passwords import hash_password
from app.security.passwords import verify_password
from app.security.jwt import decode_access_token
from app.sessions.service import create_session
from app.sessions.service import refresh_session
from app.sessions.service import revoke_session


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
    database: Session = Depends(
        get_db
    )
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
            UserRecord.email == str(
                request.email
            )
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
        email=str(
            request.email
        ),
        password_hash=hash_password(
            request.password
        ),
        team=request.team,
        role=request.role,
        active=True
    )

    database.add(
        user
    )

    database.commit()
    database.refresh(
        user
    )

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
    response_model=SessionTokenResponse
)
def login(
    request: LoginRequest,
    database: Session = Depends(
        get_db
    )
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

    return create_session(
        database,
        user
    )


@router.post(
    "/refresh",
    response_model=SessionTokenResponse
)
def refresh(
    request: RefreshRequest,
    database: Session = Depends(
        get_db
    )
):
    try:
        return refresh_session(
            database,
            request.refresh_token
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(
                exc
            )
        ) from exc


@router.post(
    "/logout",
    status_code=204
)
def logout(
    request: LogoutRequest,
    database: Session = Depends(
        get_db
    )
):
    try:
        revoke_session(
            database,
            request.refresh_token
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(
                exc
            )
        ) from exc


@router.get(
    "/me"
)
def current_identity(
    authorization: str | None = Header(
        default=None
    ),
    database: Session = Depends(
        get_db
    )
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    if not authorization.startswith(
        "Bearer "
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization scheme"
        )

    token = authorization[
        len("Bearer "):
    ].strip()

    try:
        claims = decode_access_token(
            token
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(
                exc
            )
        ) from exc

    username = claims.get(
        "sub"
    )

    user = (
        database
        .query(
            UserRecord
        )
        .filter(
            UserRecord.username
            == username
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Identity not found"
        )

    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="User account is disabled"
        )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "team": user.team,
        "role": user.role,
        "active": user.active
    }