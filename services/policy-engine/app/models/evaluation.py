from pydantic import BaseModel
from pydantic import Field


class PolicyEvaluationRequest(BaseModel):
    service_name: str = Field(
        min_length=2,
        max_length=63
    )

    owner: str = Field(
        min_length=2,
        max_length=100
    )

    repository: str

    description: str = Field(
        min_length=5,
        max_length=1000
    )

    environment: str = "development"


class PolicyViolation(BaseModel):
    rule: str
    message: str


class PolicyEvaluationResponse(BaseModel):
    decision: str
    violations: list[PolicyViolation]
