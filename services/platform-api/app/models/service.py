from pydantic import BaseModel


class Service(BaseModel):
    name: str
    owner: str
    repository: str
    lifecycle: str = "created"
