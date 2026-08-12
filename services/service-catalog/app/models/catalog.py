from pydantic import BaseModel
from pydantic import ConfigDict


class CatalogServiceCreate(BaseModel):
    name: str
    owner: str
    repository: str
    description: str
    lifecycle: str = "created"


class CatalogService(CatalogServiceCreate):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
