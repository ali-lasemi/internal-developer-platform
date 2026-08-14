from pydantic import BaseModel
from pydantic import Field


class ProvisionServiceRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=63
    )

    owner: str = Field(
        min_length=2,
        max_length=100
    )

    repository: str
    description: str
    template: str = "backend-service"
    environment: str = "development"


class ProvisionPolicyViolation(BaseModel):
    rule: str
    message: str


class ProvisionServiceResponse(BaseModel):
    service: str
    owner: str
    environment: str
    template: str
    template_version: str
    template_status: str
    policy: str
    catalog: str
    workflow: str
    status: str

    violations: list[
        ProvisionPolicyViolation
    ] = Field(
        default_factory=list
    )
