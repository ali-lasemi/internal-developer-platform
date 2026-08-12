import os

import httpx


EVENT_PLATFORM_URL = os.getenv(
    "EVENT_PLATFORM_URL",
    "http://event-platform:8000"
)


async def publish_event(
    event_type: str,
    source: str,
    subject: str,
    data: dict
):
    async with httpx.AsyncClient(
        timeout=10.0
    ) as client:
        response = await client.post(
            f"{EVENT_PLATFORM_URL}/events",
            json={
                "type": event_type,
                "source": source,
                "subject": subject,
                "data": data
            }
        )

        response.raise_for_status()

        return response.json()
