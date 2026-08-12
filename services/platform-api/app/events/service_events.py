from app.clients.event_platform import publish_event


async def publish_service_created_event(
    service_name: str,
    owner: str,
    repository: str,
    environment: str
):
    return await publish_event(
        event_type="service.created",
        source="platform-api",
        subject=service_name,
        data={
            "owner": owner,
            "repository": repository,
            "environment": environment
        }
    )


async def publish_service_provisioning_started_event(
    service_name: str,
    owner: str,
    workflow_status: str
):
    return await publish_event(
        event_type="service.provisioning.started",
        source="platform-api",
        subject=service_name,
        data={
            "owner": owner,
            "workflow_status": workflow_status
        }
    )
