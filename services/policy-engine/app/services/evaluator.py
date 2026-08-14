from urllib.parse import urlparse

from app.models.evaluation import PolicyEvaluationRequest
from app.models.evaluation import PolicyEvaluationResponse
from app.models.evaluation import PolicyViolation
from app.repository.policy_repository import policy_repository


def evaluate_service_policy(
    request: PolicyEvaluationRequest
) -> PolicyEvaluationResponse:
    policy = policy_repository.get()

    if not policy.get(
        "enabled",
        True
    ):
        return PolicyEvaluationResponse(
            decision="allowed",
            violations=[]
        )

    rules = policy.get(
        "rules",
        {}
    )

    violations: list[
        PolicyViolation
    ] = []

    service_name_rule = rules.get(
        "service-name-format",
        {}
    )

    if service_name_rule.get(
        "enabled",
        False
    ):
        valid = (
            request.service_name
            and request.service_name
            == request.service_name.lower()
            and request.service_name.replace(
                "-",
                ""
            ).isalnum()
            and "_" not in request.service_name
        )

        if not valid:
            violations.append(
                PolicyViolation(
                    rule="service-name-format",
                    message=(
                        "Service name must use lowercase "
                        "kebab-case."
                    )
                )
            )

    owner_rule = rules.get(
        "service-owner-required",
        {}
    )

    if (
        owner_rule.get(
            "enabled",
            False
        )
        and not request.owner.strip()
    ):
        violations.append(
            PolicyViolation(
                rule="service-owner-required",
                message="Service owner is required."
            )
        )

    repository_rule = rules.get(
        "repository-source",
        {}
    )

    if repository_rule.get(
        "enabled",
        False
    ):
        allowed_hosts = set(
            repository_rule.get(
                "allowed_hosts",
                []
            )
        )

        repository_host = ""

        if request.repository.startswith(
            "git@github.com:"
        ):
            repository_host = "github.com"
        else:
            repository_host = (
                urlparse(
                    request.repository
                ).hostname
                or ""
            )

        if repository_host not in allowed_hosts:
            violations.append(
                PolicyViolation(
                    rule="repository-source",
                    message=(
                        "Repository host is not "
                        "allowed by platform policy."
                    )
                )
            )

    environment_rule = rules.get(
        "environment-allowed",
        {}
    )

    if environment_rule.get(
        "enabled",
        False
    ):
        allowed_environments = set(
            environment_rule.get(
                "values",
                []
            )
        )

        if (
            request.environment
            not in allowed_environments
        ):
            violations.append(
                PolicyViolation(
                    rule="environment-allowed",
                    message=(
                        "Environment is not allowed "
                        "by platform policy."
                    )
                )
            )

    production_rule = rules.get(
        "production-description",
        {}
    )

    if (
        production_rule.get(
            "enabled",
            False
        )
        and request.environment
        == "production"
    ):
        minimum_length = int(
            production_rule.get(
                "minimum_length",
                20
            )
        )

        if (
            len(
                request.description.strip()
            )
            < minimum_length
        ):
            violations.append(
                PolicyViolation(
                    rule="production-description",
                    message=(
                        "Production service description "
                        "does not meet minimum length."
                    )
                )
            )

    return PolicyEvaluationResponse(
        decision=(
            "denied"
            if violations
            else "allowed"
        ),
        violations=violations
    )
