from datetime import datetime
from datetime import timezone

from sqlalchemy.orm import Session

from app.db.models import RefreshSessionRecord
from app.db.models import UserRecord
from app.security.jwt import create_access_token
from app.security.jwt import create_refresh_token
from app.security.jwt import decode_refresh_token


def create_session(
    database: Session,
    user: UserRecord
):
    refresh_token, token_id, expires_at = (
        create_refresh_token(
            subject=user.username
        )
    )

    session = RefreshSessionRecord(
        token_id=token_id,
        user_id=user.id,
        expires_at=expires_at,
        revoked=False
    )

    database.add(
        session
    )

    database.commit()

    access_token = create_access_token(
        subject=user.username,
        role=user.role,
        team=user.team
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def refresh_session(
    database: Session,
    refresh_token: str
):
    payload = decode_refresh_token(
        refresh_token
    )

    token_id = payload.get(
        "jti"
    )

    username = payload.get(
        "sub"
    )

    session = (
        database
        .query(RefreshSessionRecord)
        .filter(
            RefreshSessionRecord.token_id == token_id
        )
        .first()
    )

    if session is None:
        raise ValueError(
            "Session not found"
        )

    if session.revoked:
        raise ValueError(
            "Session revoked"
        )

    expires_at = session.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= datetime.now(
        timezone.utc
    ):
        raise ValueError(
            "Session expired"
        )

    user = (
        database
        .query(UserRecord)
        .filter(
            UserRecord.id == session.user_id
        )
        .first()
    )

    if user is None:
        raise ValueError(
            "User not found"
        )

    if not user.active:
        raise ValueError(
            "User disabled"
        )

    if user.username != username:
        raise ValueError(
            "Session identity mismatch"
        )

    session.revoked = True

    database.commit()

    return create_session(
        database,
        user
    )


def revoke_session(
    database: Session,
    refresh_token: str
):
    payload = decode_refresh_token(
        refresh_token
    )

    token_id = payload.get(
        "jti"
    )

    session = (
        database
        .query(RefreshSessionRecord)
        .filter(
            RefreshSessionRecord.token_id == token_id
        )
        .first()
    )

    if session is None:
        return

    session.revoked = True

    database.commit()
