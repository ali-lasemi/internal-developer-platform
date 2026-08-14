from copy import deepcopy

from app.config.policy_loader import load_policy_document


class PolicyRepository:
    def __init__(self):
        self._policy = load_policy_document()

    def get(self) -> dict:
        return deepcopy(
            self._policy
        )

    def reload(self) -> dict:
        self._policy = load_policy_document()

        return self.get()


policy_repository = PolicyRepository()
