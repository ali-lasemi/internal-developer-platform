from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator


OBJECTIVE_TYPES = {
    "availability",
    "latency",
    "error_rate"
}


class SLOBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255
    )

    objective_type: str

    target: float = Field(
        gt=0,
        le=100
    )

    window_days: int = Field(
        gt=0
    )

    latency_threshold_ms: int | None = Field(
        default=None,
        gt=0
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )

    enabled: bool = True

    observed_percentage: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    @model_validator(
        mode="after"
    )
    def validate_objective(
        self
    ):
        if (
            self.objective_type
            not in OBJECTIVE_TYPES
        ):
            raise ValueError(
                "Unsupported objective_type"
            )

        if (
            self.objective_type
            == "latency"
            and self.latency_threshold_ms
            is None
        ):
            raise ValueError(
                "latency_threshold_ms "
                "is required for latency SLO"
            )

        return self


class SLOCreate(SLOBase):
    pass


class SLOUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    objective_type: str | None = None

    target: float | None = Field(
        default=None,
        gt=0,
        le=100
    )

    window_days: int | None = Field(
        default=None,
        gt=0
    )

    latency_threshold_ms: int | None = Field(
        default=None,
        gt=0
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )

    enabled: bool | None = None

    observed_percentage: float | None = Field(
        default=None,
        ge=0,
        le=100
    )


class SLOResponse(SLOBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime


class ErrorBudgetResponse(BaseModel):
    slo_id: int
    service_id: int
    target_percentage: float
    observed_percentage: float | None
    allowed_failure_percentage: float
    window_days: int
    window_minutes: float
    allowed_failure_minutes: float
    consumed_budget_percentage: float | None
    remaining_budget_percentage: float | None
    remaining_budget_minutes: float | None
    status: str


class SLOSummaryResponse(BaseModel):
    service_id: int
    total_slos: int
    enabled_slos: int
    healthy: int
    warning: int
    exhausted: int
    unknown: int
    overall_status: str
    objectives: list[dict]