import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone

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


def create_access_token(
    subject: str,
    role: str,
    team: str
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "role": role,
        "team": team,
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


def decode_access_token(
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
            "Invalid access token"
        ) from exc
