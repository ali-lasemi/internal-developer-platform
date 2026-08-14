import os

import httpx


EVENT_PLATFORM_URL = os.getenv(
    "EVENT_PLATFORM_URL",
    "http://event-platform:8000"
)


def publish_workflow_event(
    event_type: str,
    execution_id: str,
    workflow: str,
    data: dict
):
    with httpx.Client(
        timeout=10.0
    ) as client:
        response = client.post(
            f"{EVENT_PLATFORM_URL}/events",
            json={
                "type": event_type,
                "source": "workflow-engine",
                "subject": execution_id,
                "data": {
                    "workflow": workflow,
                    **data
                }
            }
        )

        response.raise_for_status()

        return response.json()