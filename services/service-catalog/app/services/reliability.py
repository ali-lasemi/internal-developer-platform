def calculate_error_budget(
    target: float,
    window_days: int,
    observed_percentage: float | None = None
) -> dict:
    allowed_failure_percentage = (
        100.0 - target
    )

    window_minutes = (
        float(
            window_days
        )
        * 24.0
        * 60.0
    )

    allowed_failure_minutes = (
        window_minutes
        * allowed_failure_percentage
        / 100.0
    )

    result = {
        "target_percentage": target,
        "observed_percentage": (
            observed_percentage
        ),
        "allowed_failure_percentage": (
            allowed_failure_percentage
        ),
        "window_days": window_days,
        "window_minutes": window_minutes,
        "allowed_failure_minutes": (
            allowed_failure_minutes
        ),
        "consumed_budget_percentage": None,
        "remaining_budget_percentage": None,
        "remaining_budget_minutes": None,
        "status": "unknown"
    }

    if observed_percentage is None:
        return result

    observed_failure_percentage = (
        100.0
        - observed_percentage
    )

    if allowed_failure_percentage <= 0:
        if observed_failure_percentage <= 0:
            consumed = 0.0
            remaining = 100.0
            remaining_minutes = 0.0
            status = "healthy"
        else:
            consumed = 100.0
            remaining = 0.0
            remaining_minutes = 0.0
            status = "exhausted"

        result.update(
            {
                "consumed_budget_percentage": consumed,
                "remaining_budget_percentage": remaining,
                "remaining_budget_minutes": remaining_minutes,
                "status": status
            }
        )

        return result

    consumed = (
        observed_failure_percentage
        / allowed_failure_percentage
        * 100.0
    )

    remaining = (
        100.0
        - consumed
    )

    remaining_minutes = max(
        0.0,
        allowed_failure_minutes
        * remaining
        / 100.0
    )

    if remaining <= 0:
        status = "exhausted"

    elif remaining <= 25:
        status = "warning"

    else:
        status = "healthy"

    result.update(
        {
            "consumed_budget_percentage": consumed,
            "remaining_budget_percentage": remaining,
            "remaining_budget_minutes": remaining_minutes,
            "status": status
        }
    )

    return result


def summarize_slos(
    service_id: int,
    slos: list
) -> dict:
    enabled = [
        slo
        for slo in slos
        if slo.enabled
    ]

    counters = {
        "healthy": 0,
        "warning": 0,
        "exhausted": 0,
        "unknown": 0
    }

    objectives = []

    for slo in enabled:
        budget = calculate_error_budget(
            target=slo.target,
            window_days=slo.window_days,
            observed_percentage=(
                slo.observed_percentage
            )
        )

        status = budget[
            "status"
        ]

        counters[
            status
        ] += 1

        objectives.append(
            {
                "id": slo.id,
                "name": slo.name,
                "objective_type": (
                    slo.objective_type
                ),
                "target": slo.target,
                "status": status,
                "error_budget": budget
            }
        )

    if counters[
        "exhausted"
    ] > 0:
        overall = "exhausted"

    elif counters[
        "warning"
    ] > 0:
        overall = "warning"

    elif enabled and counters[
        "unknown"
    ] == len(
        enabled
    ):
        overall = "unknown"

    elif enabled:
        overall = "healthy"

    else:
        overall = "not_configured"

    return {
        "service_id": service_id,
        "total_slos": len(
            slos
        ),
        "enabled_slos": len(
            enabled
        ),
        "healthy": counters[
            "healthy"
        ],
        "warning": counters[
            "warning"
        ],
        "exhausted": counters[
            "exhausted"
        ],
        "unknown": counters[
            "unknown"
        ],
        "overall_status": overall,
        "objectives": objectives
    }