from pydantic import BaseModel


class Template(BaseModel):
    name: str
    description: str
    version: str
    type: str = "service"
