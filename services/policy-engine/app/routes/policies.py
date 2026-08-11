from fastapi import APIRouter
from app.models.policy import Policy

router = APIRouter(
    prefix="/policies",
    tags=["policies"]
)


policies = []


@router.get("")
def list_policies():
    return policies


@router.post("")
def create_policy(policy: Policy):
    policies.append(policy)
    return policy


@router.post("/evaluate")
def evaluate_policy():
    return {
        "decision": "allowed"
    }
