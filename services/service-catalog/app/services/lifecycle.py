ALLOWED_TRANSITIONS = {
    "created": {
        "development"
    },
    "development": {
        "staging",
        "deprecated"
    },
    "staging": {
        "production",
        "development",
        "deprecated"
    },
    "production": {
        "deprecated"
    },
    "deprecated": {
        "retired"
    },
    "retired": set()
}


def validate_transition(
    current: str,
    target: str
) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(
        current,
        set()
    )

    return target in allowed
