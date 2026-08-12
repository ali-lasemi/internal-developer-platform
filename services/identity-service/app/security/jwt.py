import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from uuid import uuid4

from jose import JWTError
from jose import jwt


JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change-me-in-production"
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_MINUTES",
        "60"
    )
)

REFRESH_TOKEN_DAYS = int(
    os.getenv(
        "REFRESH_TOKEN_DAYS",
        "7"
    )
)


def create_access_token(
    subject: str,
    role: str,
    team: str
) -> str:
    now = datetime.now(
        timezone.utc
    )

    payload = {
        "sub": subject,
        "role": role,
        "team": team,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_MINUTES
        )
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def create_refresh_token(
    subject: str
) -> tuple[str, str, datetime]:
    now = datetime.now(
        timezone.utc
    )

    token_id = uuid4().hex

    expires_at = now + timedelta(
        days=REFRESH_TOKEN_DAYS
    )

    payload = {
        "sub": subject,
        "jti": token_id,
        "type": "refresh",
        "iat": now,
        "exp": expires_at
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return (
        token,
        token_id,
        expires_at
    )


def decode_token(
    token: str
) -> dict:
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[
                JWT_ALGORITHM
            ]
        )

    except JWTError as exc:
        raise ValueError(
            "Invalid or expired token"
        ) from exc


def decode_access_token(
    token: str
) -> dict:
    payload = decode_token(
        token
    )

    if payload.get("type") != "access":
        raise ValueError(
            "Invalid token type"
        )

    return payload


def decode_refresh_token(
    token: str
) -> dict:
    payload = decode_token(
        token
    )

    if payload.get("type") != "refresh":
        raise ValueError(
            "Invalid token type"
        )

    return payload
