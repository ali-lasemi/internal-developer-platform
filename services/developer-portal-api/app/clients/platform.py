import os

import httpx


CATALOG_URL = os.getenv(
    "CATALOG_URL",
    "http://service-catalog:8000"
)

WORKFLOW_URL = os.getenv(
    "WORKFLOW_URL",
    "http://workflow-engine:8000"
)

IDENTITY_URL = os.getenv(
    "IDENTITY_URL",
    "http://identity-service:8000"
)

TEMPLATE_URL = os.getenv(
    "TEMPLATE_URL",
    "http://template-engine:8000"
)

POLICY_URL = os.getenv(
    "POLICY_URL",
    "http://policy-engine:8000"
)

EVENT_URL = os.getenv(
    "EVENT_URL",
    "http://event-platform:8000"
)

PLATFORM_API_URL = os.getenv(
    "PLATFORM_API_URL",
    "http://platform-api:8000"
)


async def get_json(
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


async def service_status(
    name: str,
    base_url: str
):
    try:
        health = await get_json(
            f"{base_url}/health"
        )

        return {
            "name": name,
            "status": "healthy",
            "health": health
        }

    except Exception as exc:
        return {
            "name": name,
            "status": "unavailable",
            "error": str(
                exc
            )
        }

async def post_json(
    url: str,
    payload: dict
):
    async with httpx.AsyncClient(
        timeout=5.0
    ) as client:
        response = await client.post(
            url,
            json=payload
        )

        response.raise_for_status()

        return response.json()

async def post_json_with_headers(
    url: str,
    payload: dict,
    headers: dict
):
    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:
        response = await client.post(
            url,
            json=payload,
            headers=headers
        )

        return response

async def get_json_with_headers(
    url: str,
    headers: dict
):
    async with httpx.AsyncClient(
        timeout=10.0
    ) as client:
        response = await client.get(
            url,
            headers=headers
        )

        return response