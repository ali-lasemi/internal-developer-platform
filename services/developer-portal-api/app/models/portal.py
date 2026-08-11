from pydantic import BaseModel


class PortalAction(BaseModel):
    service: str
    action: str
    user: str
