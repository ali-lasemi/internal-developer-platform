from pydantic import BaseModel


class Identity(BaseModel):
    username: str
    email: str
    team: str
    role: str = "developer"
