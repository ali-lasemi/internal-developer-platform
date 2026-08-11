from pydantic import BaseModel


class Workflow(BaseModel):
    name: str
    description: str
    status: str = "registered"
