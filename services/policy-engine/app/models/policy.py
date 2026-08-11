from pydantic import BaseModel


class Policy(BaseModel):
    name: str
    description: str
    category: str
    enabled: bool = True
