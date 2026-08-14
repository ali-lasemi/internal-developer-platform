import os

import httpx


CATALOG_URL = os.getenv(
    "CATALOG_URL",
    "http://service-catalog:8000"
)

WORKFLOW_ENGINE_URL = os.getenv(
    "WORKFLOW_ENGINE_URL",
    "http://workflow-engine:8000"
)

TEMPLATE_ENGINE_URL = os.getenv(
    "TEMPLATE_ENGINE_URL",
    "http://template-engine:8000"
)

POLICY_ENGINE_URL = os.getenv(
    "POLICY_ENGINE_URL",
    "http://policy-engine:8000"
)


async def _get(
    url: str
):
    async with httpx.AsyncClient(
        timeout=5.0
    ) as client:
        response = await client.get(
            url
        )

        response.raise_for_status()

        return response.json()


async def platform_summary():
    catalog = await _get(
        f"{CATALOG_URL}/catalog/metrics"
    )

    workflows = await _get(
        (
            f"{WORKFLOW_ENGINE_URL}"
            "/workflows/executions/metrics"
        )
    )

    templates = await _get(
        f"{TEMPLATE_ENGINE_URL}/templates"
    )

    policies = await _get(
        f"{POLICY_ENGINE_URL}/policies"
    )

    return {
        "services": catalog,
        "workflows": workflows,
        "templates": {
            "count": len(
                templates
            ),
            "items": templates
        },
        "policies": {
            "count": len(
                policies
            ),
            "items": policies
        }
    }