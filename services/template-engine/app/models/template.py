from pydantic import BaseModel
from pydantic import Field


class Template(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    description: str

    version: str

    type: str = "service"


class TemplateResolution(BaseModel):
    name: str
    version: str
    type: str
    status: str = "resolved"
