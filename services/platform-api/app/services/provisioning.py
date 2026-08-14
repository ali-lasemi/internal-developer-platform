import os

import httpx

from app.events.service_events import publish_policy_evaluated_event
from app.events.service_events import publish_service_created_event
from app.events.service_events import publish_service_provisioning_started_event
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

TEMPLATE_ENGINE_URL = os.getenv(
    "TEMPLATE_ENGINE_URL",
    "http://template-engine:8000"
)


async def provision_service(
    request: ProvisionServiceRequest
):
    async with httpx.AsyncClient(
        timeout=10.0
    ) as client:

        template_response = await client.get(
            (
                f"{TEMPLATE_ENGINE_URL}"
                f"/templates/{request.template}"
            )
        )

        if template_response.status_code == 404:
            return {
                "service": request.name,
                "owner": request.owner,
                "environment": request.environment,
                "template": request.template,
                "template_version": "unknown",
                "template_status": "not_found",
                "rendered_template": None,`r`n                "artifact_manifest": None,
                "policy": "not_evaluated",
                "catalog": "not_registered",
                "workflow": "not_started",
                "workflow_execution_id": None,
                "workflow_steps": [],
                "status": "rejected",
                "violations": []
            }

        template_response.raise_for_status()

        template_result = (
            template_response.json()
        )

        policy_response = await client.post(
            (
                f"{POLICY_ENGINE_URL}"
                "/policies/evaluate"
            ),
            json={
                "service_name": request.name,
                "owner": request.owner,
                "repository": request.repository,
                "description": request.description,
                "environment": request.environment
            }
        )

        policy_response.raise_for_status()

        policy_result = (
            policy_response.json()
        )

        decision = policy_result.get(
            "decision",
            "denied"
        )

        violations = policy_result.get(
            "violations",
            []
        )

        await publish_policy_evaluated_event(
            service_name=request.name,
            owner=request.owner,
            decision=decision,
            violations=violations
        )

        if decision != "allowed":
            return {
                "service": request.name,
                "owner": request.owner,
                "environment": request.environment,
                "template": template_result["name"],
                "template_version": template_result["version"],
                "template_status": "resolved",
                "rendered_template": None,`r`n                "artifact_manifest": None,
                "policy": "denied",
                "catalog": "not_registered",
                "workflow": "not_started",
                "workflow_execution_id": None,
                "workflow_steps": [],
                "status": "rejected",
                "violations": violations
            }

        render_response = await client.post(
            (
                f"{TEMPLATE_ENGINE_URL}"
                f"/templates/{request.template}/render"
            ),
            json={
                "name": request.name,
                "owner": request.owner,
                "repository": request.repository,
                "environment": request.environment
            }
        )

        render_response.raise_for_status()

        rendered_template = (
            render_response.json()
        )

        artifact_manifest = (
            rendered_template.get(
                "manifest"
            )
        )

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

        await publish_service_created_event(
            service_name=request.name,
            owner=request.owner,
            repository=request.repository,
            environment=request.environment
        )

        workflow_response = await client.post(
            (
                f"{WORKFLOW_ENGINE_URL}"
                "/workflows/service-creation/execute"
            )
        )

        workflow_response.raise_for_status()

        workflow_result = (
            workflow_response.json()
        )

        workflow_status = workflow_result.get(
            "status",
            "unknown"
        )

        workflow_execution_id = (
            workflow_result.get(
                "execution_id"
            )
        )

        workflow_steps = workflow_result.get(
            "steps",
            []
        )

        await publish_service_provisioning_started_event(
            service_name=request.name,
            owner=request.owner,
            workflow_status=workflow_status
        )

        return {
            "service": request.name,
            "owner": request.owner,
            "environment": request.environment,
            "template": template_result["name"],
            "template_version": template_result["version"],
            "template_status": "resolved",
            "rendered_template": rendered_template,
            "artifact_manifest": artifact_manifest,
            "policy": "allowed",
            "catalog": "registered",
            "workflow": workflow_status,
            "workflow_execution_id": workflow_execution_id,
            "workflow_steps": workflow_steps,
            "status": "provisioning",
            "violations": []
        }