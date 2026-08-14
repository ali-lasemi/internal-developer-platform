from fastapi import APIRouter

from app.models.evaluation import PolicyEvaluationRequest
from app.models.evaluation import PolicyEvaluationResponse
from app.repository.policy_repository import policy_repository
from app.services.evaluator import evaluate_service_policy


router = APIRouter(
    prefix="/policies",
    tags=["policies"]
)


@router.get("")
def get_policy():
    return policy_repository.get()


@router.post(
    "/reload"
)
def reload_policy():
    return policy_repository.reload()


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
