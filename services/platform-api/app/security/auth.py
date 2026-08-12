import os

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import JWTError
from jose import jwt


JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change-me-in-production"
)

JWT_ALGORITHM = "HS256"

security = HTTPBearer()


def current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[
                JWT_ALGORITHM
            ]
        )

        return {
            "username": payload.get(
                "sub"
            ),
            "role": payload.get(
                "role"
            ),
            "team": payload.get(
                "team"
            )
        }

    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        ) from exc


def require_roles(
    *roles: str
):
    def dependency(
        identity=Depends(
            current_identity
        )
    ):
        if identity["role"] not in roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return identity

    return dependency
