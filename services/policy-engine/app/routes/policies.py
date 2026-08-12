from fastapi import APIRouter

from app.models.evaluation import PolicyEvaluationRequest
from app.models.evaluation import PolicyEvaluationResponse
from app.models.policy import Policy
from app.services.evaluator import evaluate_service_policy


router = APIRouter(
    prefix="/policies",
    tags=["policies"]
)


policies = []


@router.get("")
def list_policies():
    return policies


@router.post("")
def create_policy(
    policy: Policy
):
    policies.append(
        policy
    )

    return policy


@router.post(
    "/evaluate",
    response_model=PolicyEvaluationResponse
)
def evaluate_policy(
    request: PolicyEvaluationRequest
):
    return evaluate_service_policy(
        request
    )
