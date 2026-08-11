from pydantic import BaseModel


class CatalogService(BaseModel):
    name: str
    owner: str
    repository: str
    description: str
    lifecycle: str = "created"
