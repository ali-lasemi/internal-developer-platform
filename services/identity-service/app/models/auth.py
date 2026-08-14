from typing import Literal

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=100
    )

    password: str = Field(
        min_length=8,
        max_length=200
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegistration(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=200
    )

    team: str = Field(
        min_length=2,
        max_length=100
    )

    role: Literal["developer"] = "developer"