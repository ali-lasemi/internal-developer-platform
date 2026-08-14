import os

import httpx


EVENT_PLATFORM_URL = os.getenv(
    "EVENT_PLATFORM_URL",
    "http://event-platform:8000"
)


async def publish_lifecycle_changed_event(
    service_name: str,
    owner: str,
    previous_lifecycle: str,
    lifecycle: str
):
    async with httpx.AsyncClient(
        timeout=10.0
    ) as client:
        response = await client.post(
            f"{EVENT_PLATFORM_URL}/events",
            json={
                "type": "service.lifecycle.changed",
                "source": "service-catalog",
                "subject": service_name,
                "data": {
                    "owner": owner,
                    "previous_lifecycle": previous_lifecycle,
                    "lifecycle": lifecycle
                }
            }
        )

        response.raise_for_status()

        return response.json()
