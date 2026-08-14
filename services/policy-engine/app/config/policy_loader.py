from pathlib import Path

import yaml


POLICY_DIRECTORY = Path(
    __file__
).resolve().parents[2] / "policies"


def load_policy_document() -> dict:
    policy_file = (
        POLICY_DIRECTORY
        / "default-service-policy.yaml"
    )

    if not policy_file.exists():
        raise RuntimeError(
            f"Policy document not found: {policy_file}"
        )

    with policy_file.open(
        "r",
        encoding="utf-8-sig"
    ) as handle:
        document = yaml.safe_load(
            handle
        )

    if not isinstance(
        document,
        dict
    ):
        raise RuntimeError(
            "Invalid policy document"
        )

    return document
