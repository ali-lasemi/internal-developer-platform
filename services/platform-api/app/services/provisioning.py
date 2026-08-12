import os

import httpx

from app.schemas.provision import ProvisionServiceRequest


POLICY_ENGINE_URL = os.getenv(
    "POLICY_ENGINE_URL",
    "http://policy-engine:8000"
)

CATALOG_URL = os.getenv(
    "CATALOG_URL",
    "http://service-catalog:8000"
)

WORKFLOW_ENGINE_URL = os.getenv(
    "WORKFLOW_ENGINE_URL",
    "http://workflow-engine:8000"
)


async def provision_service(request: ProvisionServiceRequest):
    async with httpx.AsyncClient(timeout=10.0) as client:

        policy_response = await client.post(
            f"{POLICY_ENGINE_URL}/policies/evaluate"
        )
        policy_response.raise_for_status()

        policy_decision = policy_response.json().get("decision")

        if policy_decision != "allowed":
            return {
                "service": request.name,
                "owner": request.owner,
                "environment": request.environment,
                "policy": policy_decision,
                "catalog": "not_registered",
                "workflow": "not_started",
                "status": "rejected"
            }

        catalog_response = await client.post(
            f"{CATALOG_URL}/catalog",
            json={
                "name": request.name,
                "owner": request.owner,
                "repository": request.repository,
                "description": request.description,
                "lifecycle": "created"
            }
        )
        catalog_response.raise_for_status()

        workflow_response = await client.post(
            f"{WORKFLOW_ENGINE_URL}/workflows/service-creation/execute"
        )
        workflow_response.raise_for_status()

        workflow_status = workflow_response.json().get(
            "status",
            "unknown"
        )

        return {
            "service": request.name,
            "owner": request.owner,
            "environment": request.environment,
            "policy": "allowed",
            "catalog": "registered",
            "workflow": workflow_status,
            "status": "provisioning"
        }
