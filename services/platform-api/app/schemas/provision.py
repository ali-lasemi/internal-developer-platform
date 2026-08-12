from pydantic import BaseModel, Field


class ProvisionServiceRequest(BaseModel):
    name: str = Field(min_length=2, max_length=63)
    owner: str = Field(min_length=2, max_length=100)
    repository: str
    description: str
    template: str = "backend-service"
    environment: str = "development"


class ProvisionServiceResponse(BaseModel):
    service: str
    owner: str
    environment: str
    policy: str
    catalog: str
    workflow: str
    status: str
