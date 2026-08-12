import re

from app.models.evaluation import PolicyEvaluationRequest
from app.models.evaluation import PolicyEvaluationResponse
from app.models.evaluation import PolicyViolation


SERVICE_NAME_PATTERN = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
)

ALLOWED_ENVIRONMENTS = {
    "development",
    "staging",
    "production"
}


def evaluate_service_policy(
    request: PolicyEvaluationRequest
) -> PolicyEvaluationResponse:
    violations: list[PolicyViolation] = []

    if not SERVICE_NAME_PATTERN.match(
        request.service_name
    ):
        violations.append(
            PolicyViolation(
                rule="service-name-format",
                message=(
                    "Service name must use lowercase "
                    "kebab-case."
                )
            )
        )

    if not request.owner.strip():
        violations.append(
            PolicyViolation(
                rule="service-owner-required",
                message="Service owner is required."
            )
        )

    if not (
        request.repository.startswith(
            "https://github.com/"
        )
        or request.repository.startswith(
            "git@github.com:"
        )
    ):
        violations.append(
            PolicyViolation(
                rule="repository-source",
                message=(
                    "Repository must be hosted on GitHub."
                )
            )
        )

    if request.environment not in ALLOWED_ENVIRONMENTS:
        violations.append(
            PolicyViolation(
                rule="environment-allowed",
                message=(
                    "Environment must be development, "
                    "staging, or production."
                )
            )
        )

    if (
        request.environment == "production"
        and len(request.description.strip()) < 20
    ):
        violations.append(
            PolicyViolation(
                rule="production-description",
                message=(
                    "Production services require a "
                    "meaningful description."
                )
            )
        )

    decision = (
        "denied"
        if violations
        else "allowed"
    )

    return PolicyEvaluationResponse(
        decision=decision,
        violations=violations
    )
